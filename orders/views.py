from django.db import transaction
from django.utils import timezone
from catalog.models import ProductVariant

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
    class SimulatePaymentView(APIView):
        permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, order_id):
        try:
            order = Order.objects.select_for_update().get(
                id=order_id,
                user=request.user
            )
        except Order.DoesNotExist:
            return Response(
                {'detail': 'Orden no encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if order.status != Order.STATUS_PENDING:
            return Response(
                {'detail': 'Esta orden ya fue pagada o no está pendiente.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        order_items = order.items.select_related('variant', 'variant__product')

        for item in order_items:
            if item.variant is None:
                return Response(
                    {
                        'detail': f'La variante del producto {item.product_name} ya no existe.'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            variant = ProductVariant.objects.select_for_update().get(
                id=item.variant.id
            )

            if item.quantity > variant.stock:
                return Response(
                    {
                        'detail': f'No hay stock suficiente para {item.product_name}. Stock disponible: {variant.stock}.'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        for item in order_items:
            variant = ProductVariant.objects.select_for_update().get(
                id=item.variant.id
            )
            variant.stock -= item.quantity
            variant.save()

        order.status = Order.STATUS_PAID
        order.paid_at = timezone.now()
        order.save()

        serializer = OrderSerializer(order)
        return Response(
            {
                'detail': 'Pago simulado correctamente. Stock descontado.',
                'order': serializer.data
            },
            status=status.HTTP_200_OK
        )