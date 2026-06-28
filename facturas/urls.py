from django.urls import path

from .views import FacturaPDFView


urlpatterns = [
    path(
        'orders/<int:order_id>/pdf/',
        FacturaPDFView.as_view(),
        name='factura-pdf'
    ),
]