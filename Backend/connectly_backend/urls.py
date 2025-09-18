from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # Authentication
    path('api/auth/', include('dj_rest_auth.urls')),
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),

    # Social login
    path('api/auth/social/', include('connectly_backend.social_urls')),  # 👈 our custom file

    # App routes
    path('api/', include('posts.urls')),
]
