from django.urls import path

from .views import (
    OrderListView,
    OrderDetailView,
    CheckoutView,
    SimulatePaymentView,
    AdminOrderListView,
    AdminOrderStatusView,
)
urlpatterns = [
    path(
        '',
        OrderListView.as_view(),
        name='order-list'
    ),
    path(
        'checkout/',
        CheckoutView.as_view(),
        name='order-checkout'
    ),
    path(
        'admin/',
        AdminOrderListView.as_view(),
        name='admin-order-list'
    ),
    path(
        'admin/<int:order_id>/status/',
        AdminOrderStatusView.as_view(),
        name='admin-order-status'
    ),
    path(
        '<int:order_id>/',
        OrderDetailView.as_view(),
        name='order-detail'
    ),
    path(
        '<int:order_id>/pay/',
        SimulatePaymentView.as_view(),
        name='order-pay'
    ),
]