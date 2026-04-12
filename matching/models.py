from django.db import models
from django.conf import settings
from django.utils import timezone


class Swipe(models.Model):
    SWIPE_CHOICES = [
        ('like', 'Like'),
        ('dislike', 'Dislike'),
        ('superlike', 'Super Like'),
    ]

    swiper = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='swipes_made')
    swiped = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='swipes_received')
    direction = models.CharField(max_length=10, choices=SWIPE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'swipes'
        unique_together = ['swiper', 'swiped']

    def __str__(self):
        return f"{self.swiper} -> {self.swiped}: {self.direction}"


class Match(models.Model):
    user1 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='matches_as_user1')
    user2 = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='matches_as_user2')
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'matches'
        unique_together = ['user1', 'user2']

    def __str__(self):
        return f"Match: {self.user1} & {self.user2}"

    def get_other_user(self, user):
        return self.user2 if self.user1 == user else self.user1

    @classmethod
    def get_match_between(cls, user_a, user_b):
        return cls.objects.filter(
            models.Q(user1=user_a, user2=user_b) |
            models.Q(user1=user_b, user2=user_a)
        ).first()
