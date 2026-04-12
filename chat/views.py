from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Q
from django.views.decorators.http import require_POST
from .models import Message, Report
from accounts.models import User
from matching.models import Match
from profiles.models import Profile


@login_required
def chat_room(request, user_id):
    other_user = get_object_or_404(User, pk=user_id)

    # Verify they are matched
    match = Match.objects.filter(
        Q(user1=request.user, user2=other_user) |
        Q(user1=other_user, user2=request.user),
        is_active=True
    ).first()

    if not match:
        return redirect('matching:matches')

    # Load message history
    messages_qs = Message.objects.filter(
        Q(sender=request.user, receiver=other_user) |
        Q(sender=other_user, receiver=request.user)
    ).order_by('created_at')

    # Mark received messages as read
    Message.objects.filter(sender=other_user, receiver=request.user, is_read=False).update(is_read=True)

    try:
        other_profile = other_user.profile
    except Profile.DoesNotExist:
        other_profile = None

    return render(request, 'chat/chat_room.html', {
        'other_user': other_user,
        'other_profile': other_profile,
        'messages': messages_qs,
        'match': match,
    })


@login_required
@require_POST
def report_user(request, user_id):
    reported = get_object_or_404(User, pk=user_id)
    reason = request.POST.get('reason', 'other')
    details = request.POST.get('details', '')
    Report.objects.create(
        reporter=request.user,
        reported=reported,
        reason=reason,
        details=details
    )
    return JsonResponse({'status': 'reported'})


@login_required
def unread_count(request):
    count = Message.objects.filter(receiver=request.user, is_read=False).count()
    return JsonResponse({'count': count})
