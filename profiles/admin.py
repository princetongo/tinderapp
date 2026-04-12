from django.contrib import admin
from .models import Profile, ProfilePhoto, Interest, ProfileInterest


class PhotoInline(admin.TabularInline):
    model = ProfilePhoto
    extra = 0


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'first_name', 'age', 'gender', 'location', 'is_complete', 'is_verified']
    list_filter = ['gender', 'interested_in', 'is_complete', 'is_verified']
    search_fields = ['user__email', 'first_name', 'location']
    inlines = [PhotoInline]


@admin.register(Interest)
class InterestAdmin(admin.ModelAdmin):
    list_display = ['name', 'emoji']
