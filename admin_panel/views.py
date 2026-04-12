from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from accounts.models import User
from profiles.models import Profile
from matching.models import Match, Swipe
from chat.models import Message, Report


def is_admin(user):
    return user.is_authenticated and (user.is_admin or user.is_staff)


admin_required = user_passes_test(is_admin, login_url='/accounts/login/')


@login_required
@admin_required
def dashboard(request):
    now = timezone.now()
    week_ago = now - timedelta(days=7)

    stats = {
        'total_users': User.objects.count(),
        'active_users': User.objects.filter(last_seen__gte=week_ago).count(),
        'banned_users': User.objects.filter(is_banned=True).count(),
        'total_matches': Match.objects.filter(is_active=True).count(),
        'new_matches_week': Match.objects.filter(created_at__gte=week_ago).count(),
        'total_messages': Message.objects.count(),
        'pending_reports': Report.objects.filter(is_reviewed=False).count(),
        'total_swipes': Swipe.objects.count(),
        'likes_week': Swipe.objects.filter(direction__in=['like', 'superlike'], created_at__gte=week_ago).count(),
    }

    recent_users = User.objects.order_by('-date_joined')[:10]
    pending_reports = Report.objects.filter(is_reviewed=False).select_related('reporter', 'reported')[:5]

    return render(request, 'admin_panel/dashboard.html', {
        'stats': stats,
        'recent_users': recent_users,
        'pending_reports': pending_reports,
    })


@login_required
@admin_required
def user_list(request):
    query = request.GET.get('q', '')
    filter_type = request.GET.get('filter', 'all')

    users = User.objects.select_related('profile').order_by('-date_joined')

    if query:
        users = users.filter(Q(email__icontains=query) | Q(username__icontains=query))

    if filter_type == 'banned':
        users = users.filter(is_banned=True)
    elif filter_type == 'active':
        users = users.filter(is_active=True, is_banned=False)
    elif filter_type == 'incomplete':
        users = users.filter(profile__is_complete=False)

    return render(request, 'admin_panel/user_list.html', {
        'users': users,
        'query': query,
        'filter_type': filter_type,
    })


@login_required
@admin_required
def user_detail(request, user_id):
    target = get_object_or_404(User, pk=user_id)
    try:
        profile = target.profile
    except Profile.DoesNotExist:
        profile = None

    matches = Match.objects.filter(
        Q(user1=target) | Q(user2=target)
    ).select_related('user1__profile', 'user2__profile')

    reports_received = Report.objects.filter(reported=target).select_related('reporter')
    swipe_stats = Swipe.objects.filter(swiper=target).values('direction').annotate(count=Count('direction'))

    return render(request, 'admin_panel/user_detail.html', {
        'target': target,
        'profile': profile,
        'matches': matches,
        'reports_received': reports_received,
        'swipe_stats': swipe_stats,
    })


@login_required
@admin_required
def ban_user(request, user_id):
    target = get_object_or_404(User, pk=user_id)
    if target.is_staff:
        messages.error(request, "Cannot ban staff users.")
        return redirect('admin_panel:user_detail', user_id=user_id)
    target.is_banned = True
    target.is_active = False
    target.save()
    messages.success(request, f"{target.email} has been banned.")
    return redirect('admin_panel:user_detail', user_id=user_id)


@login_required
@admin_required
def unban_user(request, user_id):
    target = get_object_or_404(User, pk=user_id)
    target.is_banned = False
    target.is_active = True
    target.save()
    messages.success(request, f"{target.email} has been unbanned.")
    return redirect('admin_panel:user_detail', user_id=user_id)


@login_required
@admin_required
def verify_profile(request, user_id):
    profile = get_object_or_404(Profile, user_id=user_id)
    profile.is_verified = not profile.is_verified
    profile.save()
    status = "verified" if profile.is_verified else "unverified"
    messages.success(request, f"Profile {status}.")
    return redirect('admin_panel:user_detail', user_id=user_id)


@login_required
@admin_required
def reports_list(request):
    filter_type = request.GET.get('filter', 'pending')
    reports = Report.objects.select_related('reporter', 'reported').order_by('-created_at')

    if filter_type == 'pending':
        reports = reports.filter(is_reviewed=False)
    elif filter_type == 'reviewed':
        reports = reports.filter(is_reviewed=True)

    return render(request, 'admin_panel/reports.html', {
        'reports': reports,
        'filter_type': filter_type,
    })


@login_required
@admin_required
def review_report(request, report_id):
    report = get_object_or_404(Report, pk=report_id)
    report.is_reviewed = True
    report.save()
    messages.success(request, "Report marked as reviewed.")
    return redirect('admin_panel:reports')


@login_required
@admin_required
def delete_match(request, match_id):
    match = get_object_or_404(Match, pk=match_id)
    match.is_active = False
    match.save()
    messages.success(request, "Match deactivated.")
    return redirect('admin_panel:dashboard')
