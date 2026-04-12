from django.urls import path
from . import views

app_name = 'admin_panel'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('users/', views.user_list, name='user_list'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('users/<int:user_id>/ban/', views.ban_user, name='ban_user'),
    path('users/<int:user_id>/unban/', views.unban_user, name='unban_user'),
    path('users/<int:user_id>/verify/', views.verify_profile, name='verify_profile'),
    path('reports/', views.reports_list, name='reports'),
    path('reports/<int:report_id>/review/', views.review_report, name='review_report'),
    path('matches/<int:match_id>/delete/', views.delete_match, name='delete_match'),
]
