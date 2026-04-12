from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('<int:user_id>/', views.chat_room, name='chat_room'),
    path('report/<int:user_id>/', views.report_user, name='report_user'),
    path('unread/', views.unread_count, name='unread_count'),
]
