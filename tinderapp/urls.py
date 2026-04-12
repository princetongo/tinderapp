from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin-panel/', admin.site.urls),
    path('', RedirectView.as_view(url='/profiles/discover/', permanent=False)),
    path('accounts/', include('accounts.urls')),
    path('profiles/', include('profiles.urls')),
    path('matching/', include('matching.urls')),
    path('chat/', include('chat.urls')),
    path('admin-panel/', include('admin_panel.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
