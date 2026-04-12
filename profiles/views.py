from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import Profile, ProfilePhoto, Interest
from .forms import ProfileForm, PhotoUploadForm
from matching.models import Swipe, Match


@login_required
def discover(request):
    """Main swiping view - show profiles not yet swiped."""
    try:
        my_profile = request.user.profile
    except Profile.DoesNotExist:
        return redirect('profiles:edit_profile')

    # Get IDs already swiped
    swiped_ids = Swipe.objects.filter(swiper=request.user).values_list('swiped_id', flat=True)
    # Blocked
    blocked_ids = list(swiped_ids)

    # Filter by interest
    gender_filter = Q()
    if my_profile.interested_in == 'M':
        gender_filter = Q(gender='M')
    elif my_profile.interested_in == 'W':
        gender_filter = Q(gender='W')

    profiles = Profile.objects.filter(
        gender_filter,
        is_complete=True,
    ).exclude(
        user=request.user
    ).exclude(
        user_id__in=blocked_ids
    ).exclude(
        user__is_banned=True
    ).select_related('user').prefetch_related('photos')[:20]

    return render(request, 'profiles/discover.html', {
        'profiles': profiles,
        'my_profile': my_profile,
    })


@login_required
def profile_detail(request, pk):
    profile = get_object_or_404(Profile, pk=pk)
    return render(request, 'profiles/profile_detail.html', {'profile': profile})


@login_required
def edit_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)
    interests = Interest.objects.all()
    user_interest_ids = list(profile.profile_interests.values_list('interest_id', flat=True))

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            p = form.save(commit=False)
            # Mark complete if minimum fields filled
            if p.first_name and p.birth_date and p.gender:
                p.is_complete = True
            p.save()

            # Handle interests
            selected_interests = request.POST.getlist('interests')
            from .models import ProfileInterest
            ProfileInterest.objects.filter(profile=profile).delete()
            for interest_id in selected_interests:
                try:
                    interest = Interest.objects.get(id=interest_id)
                    ProfileInterest.objects.create(profile=profile, interest=interest)
                except Interest.DoesNotExist:
                    pass

            messages.success(request, 'Profile updated!')
            return redirect('profiles:discover')
    else:
        form = ProfileForm(instance=profile)

    return render(request, 'profiles/edit_profile.html', {
        'form': form,
        'interests': interests,
        'user_interest_ids': user_interest_ids,
        'profile': profile,
    })


@login_required
def upload_photo(request):
    if request.method == 'POST':
        form = PhotoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            profile = get_object_or_404(Profile, user=request.user)
            photo = form.save(commit=False)
            photo.profile = profile
            if form.cleaned_data['is_primary']:
                # Un-primary others
                ProfilePhoto.objects.filter(profile=profile).update(is_primary=False)
            photo.save()
            messages.success(request, 'Photo uploaded!')
            return redirect('profiles:edit_profile')
    return redirect('profiles:edit_profile')


@login_required
def delete_photo(request, pk):
    photo = get_object_or_404(ProfilePhoto, pk=pk, profile__user=request.user)
    photo.delete()
    messages.success(request, 'Photo deleted.')
    return redirect('profiles:edit_profile')


@login_required
def set_primary_photo(request, pk):
    profile = get_object_or_404(Profile, user=request.user)
    ProfilePhoto.objects.filter(profile=profile).update(is_primary=False)
    photo = get_object_or_404(ProfilePhoto, pk=pk, profile=profile)
    photo.is_primary = True
    photo.save()
    return JsonResponse({'status': 'ok'})
