from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.views import RecipeViewSet

router = DefaultRouter()

router.register('recipes', RecipeViewSet, 'recipes')

urlpatterns = [
    path('', include(router.urls)),
]
