from django.db import transaction

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from cart.models import Cart
from .models import Order, OrderItem
from .serializers import OrderSerializer


class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, order_id):
        try:
            order = Order.objects.get(id=order_id, user=request.user)
        except Order.DoesNotExist:
            return Response(
                {'detail': 'Orden no encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = OrderSerializer(order)
        return Response(serializer.data)


class CheckoutView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)

        if not cart.items.exists():
            return Response(
                {'detail': 'Tu carrito está vacío.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        for item in cart.items.select_related('variant', 'variant__product'):
            if item.quantity > item.variant.stock:
                return Response(
                    {
                        'detail': f'No hay stock suficiente para {item.variant}. Stock disponible: {item.variant.stock}.'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        order = Order.objects.create(
            user=request.user,
            status=Order.STATUS_PENDING
        )

        for item in cart.items.select_related('variant', 'variant__product'):
            variant = item.variant

            OrderItem.objects.create(
                order=order,
                variant=variant,
                product_name=variant.product.name,
                variant_size=variant.size,
                variant_color=variant.color,
                unit_price=variant.final_price,
                quantity=item.quantity
            )

        cart.items.all().delete()

        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
