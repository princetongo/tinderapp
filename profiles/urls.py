from django.urls import path
from . import views

app_name = 'profiles'

urlpatterns = [
    path('discover/', views.discover, name='discover'),
    path('<int:pk>/', views.profile_detail, name='profile_detail'),
    path('edit/', views.edit_profile, name='edit_profile'),
    path('photo/upload/', views.upload_photo, name='upload_photo'),
    path('photo/<int:pk>/delete/', views.delete_photo, name='delete_photo'),
    path('photo/<int:pk>/set-primary/', views.set_primary_photo, name='set_primary_photo'),
]
