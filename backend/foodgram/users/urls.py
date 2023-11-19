from django.urls import include, path

urlpatterns = [
    path('api/auth/token', include('api.urls')),
]
