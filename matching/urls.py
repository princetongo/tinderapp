from django.urls import path
from . import views

app_name = 'matching'

urlpatterns = [
    path('swipe/', views.swipe, name='swipe'),
    path('matches/', views.matches_list, name='matches'),
    path('unmatch/<int:match_id>/', views.unmatch, name='unmatch'),
]
