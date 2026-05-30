from django.urls import path

from .views import (
    CartDetailView,
    AddCartItemView,
    UpdateCartItemView,
    RemoveCartItemView,
    ClearCartView,
)


urlpatterns = [
    path('', CartDetailView.as_view(), name='cart-detail'),
    path('add/', AddCartItemView.as_view(), name='cart-add'),
    path('items/<int:item_id>/', UpdateCartItemView.as_view(), name='cart-update-item'),
    path('items/<int:item_id>/remove/', RemoveCartItemView.as_view(), name='cart-remove-item'),
    path('clear/', ClearCartView.as_view(), name='cart-clear'),
]