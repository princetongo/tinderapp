from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.http import require_POST
import json

from .models import Swipe, Match
from accounts.models import User
from profiles.models import Profile


@login_required
@require_POST
def swipe(request):
    """Handle like/dislike/superlike swipe action."""
    try:
        data = json.loads(request.body)
        swiped_id = data.get('swiped_id')
        direction = data.get('direction')

        if direction not in ['like', 'dislike', 'superlike']:
            return JsonResponse({'error': 'Invalid direction'}, status=400)

        swiped_user = get_object_or_404(User, pk=swiped_id)

        if swiped_user == request.user:
            return JsonResponse({'error': 'Cannot swipe yourself'}, status=400)

        swipe_obj, created = Swipe.objects.get_or_create(
            swiper=request.user,
            swiped=swiped_user,
            defaults={'direction': direction}
        )
        if not created:
            swipe_obj.direction = direction
            swipe_obj.save()

        # Check for mutual like = match
        matched = False
        if direction in ['like', 'superlike']:
            mutual = Swipe.objects.filter(
                swiper=swiped_user,
                swiped=request.user,
                direction__in=['like', 'superlike']
            ).exists()

            if mutual:
                # Create match (avoid duplicates)
                user1, user2 = sorted([request.user, swiped_user], key=lambda u: u.id)
                match, match_created = Match.objects.get_or_create(user1=user1, user2=user2)
                matched = match_created or match.is_active

        return JsonResponse({
            'status': 'ok',
            'matched': matched,
            'match_name': swiped_user.profile.first_name if matched else None,
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def matches_list(request):
    """Show all matches for current user."""
    matches = Match.objects.filter(
        Q(user1=request.user) | Q(user2=request.user),
        is_active=True
    ).select_related('user1__profile', 'user2__profile').order_by('-created_at')

    match_data = []
    for match in matches:
        other = match.get_other_user(request.user)
        from chat.models import Message
        last_msg = Message.objects.filter(
            Q(sender=request.user, receiver=other) |
            Q(sender=other, receiver=request.user)
        ).order_by('-created_at').first()

        try:
            other_profile = other.profile
        except Profile.DoesNotExist:
            continue

        match_data.append({
            'match': match,
            'other_user': other,
            'other_profile': other_profile,
            'last_message': last_msg,
        })

    return render(request, 'matching/matches.html', {'match_data': match_data})


@login_required
def unmatch(request, match_id):
    match = get_object_or_404(Match, pk=match_id)
    if request.user not in [match.user1, match.user2]:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    match.is_active = False
    match.save()
    return JsonResponse({'status': 'unmatched'})
