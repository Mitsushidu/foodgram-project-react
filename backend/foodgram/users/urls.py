from django.urls import path, include

urlpatterns = [
    path('api/auth/token', include('api.urls')),
]
