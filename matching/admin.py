from django.contrib import admin
from .models import Swipe, Match


@admin.register(Swipe)
class SwipeAdmin(admin.ModelAdmin):
    list_display = ['swiper', 'swiped', 'direction', 'created_at']
    list_filter = ['direction']
    search_fields = ['swiper__email', 'swiped__email']


@admin.register(Match)
class MatchAdmin(admin.ModelAdmin):
    list_display = ['user1', 'user2', 'created_at', 'is_active']
    list_filter = ['is_active']
    search_fields = ['user1__email', 'user2__email']
