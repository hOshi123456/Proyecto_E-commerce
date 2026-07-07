from decimal import Decimal

from django.db import transaction
from django.utils import timezone

from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from cart.models import Cart
from catalog.models import ProductVariant
from cupones.models import Cupon

from .models import Order, OrderItem


from .serializers import (
    AdminOrderStatusResponseSerializer,
    CheckoutSerializer,
    OrderSerializer,
    OrderStatusUpdateSerializer,
    PaymentResponseSerializer,
)

from drf_spectacular.utils import extend_schema



class OrderListView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Órdenes'],
        summary='Listar órdenes del usuario',
        responses={200: OrderSerializer(many=True)},
    )
    def get(self, request):
        orders = Order.objects.filter(user=request.user)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)


class OrderDetailView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Órdenes'],
        summary='Detalles de una orden',
        responses={200: OrderSerializer},
    )
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

    @extend_schema(
        tags=['Órdenes'],
        summary='Crear orden desde el carrito',
        description='Permite aplicar opcionalmente un cupón.',
        request=CheckoutSerializer,
        responses={201: OrderSerializer},
    )
    @transaction.atomic
    def post(self, request):
        input_serializer = CheckoutSerializer(
            data=request.data
        )
        input_serializer.is_valid(raise_exception=True)

        cupon_code = input_serializer.validated_data.get(
            'cupon_code',
            ''
        ).strip().upper()

        cart, created = Cart.objects.get_or_create(
            user=request.user
        )

        cart_items = list(
            cart.items.select_related(
                'variant',
                'variant__product'
            )
        )

        if not cart_items:
            return Response(
                {'detail': 'Tu carrito está vacío.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        for item in cart_items:
            if item.quantity > item.variant.stock:
                return Response(
                    {
                        'detail': (
                            f'No hay stock suficiente para '
                            f'{item.variant}. '
                            f'Stock disponible: '
                            f'{item.variant.stock}.'
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        cart_subtotal = sum(
            (item.subtotal for item in cart_items),
            Decimal('0.00')
        )

        cupon = None
        discount_amount = Decimal('0.00')

        if cupon_code:
            try:
                cupon = Cupon.objects.get(
                    code=cupon_code
                )
            except Cupon.DoesNotExist:
                return Response(
                    {
                        'detail': (
                            'El cupón ingresado no existe.'
                        )
                    },
                    status=status.HTTP_404_NOT_FOUND
                )

            if not cupon.is_valid():
                return Response(
                    {
                        'detail': (
                            'El cupón no está disponible.'
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            if (
                cart_subtotal
                < cupon.minimum_order_amount
            ):
                return Response(
                    {
                        'detail': (
                            'El carrito no alcanza el monto '
                            'mínimo requerido por el cupón.'
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            discount_amount = (
                cupon.calculate_discount(cart_subtotal)
            )

        order = Order.objects.create(
            user=request.user,
            status=Order.STATUS_PENDING,
            cupon=cupon,
            cupon_code=cupon.code if cupon else '',
            discount_amount=discount_amount
        )

        for item in cart_items:
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

        return Response(
            serializer.data,
            status=status.HTTP_201_CREATED
        )
    
class SimulatePaymentView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Órdenes'],
        summary='Simular pago de una orden',
        description=(
            'Marca una orden pendiente como pagada, '
            'descuenta el stock y registra el uso del cupón.'
        ),
        request=None,
        responses={
            200: PaymentResponseSerializer,
        },
    )
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
                {
                    'detail': (
                        'Esta orden ya fue pagada '
                        'o no está pendiente.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        cupon = None

        if order.cupon_id:
            cupon = Cupon.objects.select_for_update().get(
                id=order.cupon_id
            )

            if not cupon.is_valid():
                return Response(
                    {
                        'detail': (
                            'El cupón de esta orden '
                            'ya no está disponible.'
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        order_items = list(
            order.items.select_related(
                'variant',
                'variant__product'
            )
        )

        for item in order_items:
            if item.variant is None:
                return Response(
                    {
                        'detail': (
                            f'La variante del producto '
                            f'{item.product_name} ya no existe.'
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            variant = ProductVariant.objects.select_for_update().get(
                id=item.variant.id
            )

            if item.quantity > variant.stock:
                return Response(
                    {
                        'detail': (
                            f'No hay stock suficiente para '
                            f'{item.product_name}. '
                            f'Stock disponible: {variant.stock}.'
                        )
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        for item in order_items:
            variant = ProductVariant.objects.select_for_update().get(
                id=item.variant.id
            )

            variant.stock -= item.quantity
            variant.save(update_fields=['stock'])

        if cupon:
            cupon.times_used += 1
            cupon.save(update_fields=['times_used'])

        order.status = Order.STATUS_PAID
        order.paid_at = timezone.now()
        order.save(
            update_fields=[
                'status',
                'paid_at',
                'updated_at',
            ]
        )

        serializer = OrderSerializer(order)

        return Response(
            {
                'detail': (
                    'Pago simulado correctamente. '
                    'Stock descontado.'
                ),
                'order': serializer.data
            },
            status=status.HTTP_200_OK
        )
     
class AdminOrderListView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        tags=['Órdenes'],
        summary='Listar todas las órdenes (admin)',
        responses={200: OrderSerializer(many=True)},
    )
    def get(self, request):
        orders = (
            Order.objects
            .select_related('user', 'cupon')
            .prefetch_related('items')
            .all()
        )

        serializer = OrderSerializer(
            orders,
            many=True
        )

        return Response(serializer.data)


class AdminOrderStatusView(APIView):
    permission_classes = [IsAdminUser]

    @extend_schema(
        tags=['Órdenes - Administración'],
        summary='Actualizar estado de una orden',
        description=(
            'Permite al administrador cancelar, enviar '
            'o marcar una orden como entregada.'
        ),
        request=OrderStatusUpdateSerializer,
        responses={
            200: AdminOrderStatusResponseSerializer,
        },
    )
    @transaction.atomic

    @extend_schema(
        tags=['Órdenes'],
        summary='Actualizar estado de una orden (admin)',
        responses={200: OrderSerializer},
    )
    @transaction.atomic
    def patch(self, request, order_id):
        try:
            order = Order.objects.select_for_update().get(
                id=order_id
            )
        except Order.DoesNotExist:
            return Response(
                {'detail': 'Orden no encontrada.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = OrderStatusUpdateSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        new_status = serializer.validated_data['status']

        allowed_transitions = {
            Order.STATUS_PENDING: {
                Order.STATUS_CANCELLED,
            },
            Order.STATUS_PAID: {
                Order.STATUS_SHIPPED,
            },
            Order.STATUS_SHIPPED: {
                Order.STATUS_DELIVERED,
            },
        }

        valid_statuses = allowed_transitions.get(
            order.status,
            set()
        )

        if new_status not in valid_statuses:
            return Response(
                {
                    'detail': (
                        f'No se puede cambiar una orden '
                        f'de {order.status} a {new_status}.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        order.status = new_status
        order.save(
            update_fields=[
                'status',
                'updated_at',
            ]
        )

        return Response({
            'detail': 'Estado actualizado correctamente.',
            'order': OrderSerializer(order).data,
        })