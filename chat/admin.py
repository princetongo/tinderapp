from django.contrib import admin
from .models import Message, Report


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['sender', 'receiver', 'content', 'is_read', 'created_at']
    list_filter = ['is_read']
    search_fields = ['sender__email', 'receiver__email']


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ['reporter', 'reported', 'reason', 'is_reviewed', 'created_at']
    list_filter = ['reason', 'is_reviewed']
    search_fields = ['reporter__email', 'reported__email']
    actions = ['mark_reviewed']

    def mark_reviewed(self, request, queryset):
        queryset.update(is_reviewed=True)
    mark_reviewed.short_description = 'Mark selected reports as reviewed'
