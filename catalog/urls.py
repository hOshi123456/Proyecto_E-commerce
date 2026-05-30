from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import CategoryViewSet, ProductViewSet, ProductVariantViewSet


router = DefaultRouter()
router.register('categories', CategoryViewSet)
router.register('products', ProductViewSet)
router.register('variants', ProductVariantViewSet)

urlpatterns = [
    path('', include(router.urls)),
]