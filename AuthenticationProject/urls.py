from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # --- JWT Authentication Endpoints ---
    # User yahan username/password bhejega aur Token payega
    path('api/login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    # Purana access token expire hone par naya lene ke liye
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # --- Aapki App ke URLs ---
    path('', include('Core.urls')),
]

# Render par images aur CSS sahi se dikhane ke liye ye zaroori hai
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)