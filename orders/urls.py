from django.urls import path

from .views import (
    OrderListView,
    OrderDetailView,
    CheckoutView,
    SimulatePaymentView,
)


urlpatterns = [
    path('', OrderListView.as_view(), name='order-list'),
    path('checkout/', CheckoutView.as_view(), name='order-checkout'),
    path('<int:order_id>/', OrderDetailView.as_view(), name='order-detail'),
    path('<int:order_id>/pay/', SimulatePaymentView.as_view(), name='order-pay'),
]