from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import CuponValidationView, CuponViewSet


router = DefaultRouter()
router.register('', CuponViewSet, basename='cupon')


urlpatterns = [
    path(
        'validate/',
        CuponValidationView.as_view(),
        name='cupon-validate'
    ),
    path('', include(router.urls)),
]