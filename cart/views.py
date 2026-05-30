from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .models import Cart, CartItem
from .serializers import (
    CartSerializer,
    AddCartItemSerializer,
    UpdateCartItemSerializer,
)


class CartDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        serializer = CartSerializer(cart)
        return Response(serializer.data)


class AddCartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = AddCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        variant = serializer.validated_data['variant']
        quantity = serializer.validated_data['quantity']

        cart, created = Cart.objects.get_or_create(user=request.user)

        item, created = CartItem.objects.get_or_create(
            cart=cart,
            variant=variant,
            defaults={'quantity': quantity}
        )

        if not created:
            new_quantity = item.quantity + quantity

            if new_quantity > variant.stock:
                return Response(
                    {
                        'detail': f'No podés agregar esa cantidad. Stock disponible: {variant.stock}.'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            item.quantity = new_quantity
            item.save()

        cart_serializer = CartSerializer(cart)
        return Response(cart_serializer.data, status=status.HTTP_201_CREATED)


class UpdateCartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, item_id):
        cart, created = Cart.objects.get_or_create(user=request.user)

        try:
            item = CartItem.objects.get(id=item_id, cart=cart)
        except CartItem.DoesNotExist:
            return Response(
                {'detail': 'Item no encontrado en tu carrito.'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = UpdateCartItemSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        quantity = serializer.validated_data['quantity']

        if quantity > item.variant.stock:
            return Response(
                {
                    'detail': f'Solo hay {item.variant.stock} unidades disponibles.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        item.quantity = quantity
        item.save()

        cart_serializer = CartSerializer(cart)
        return Response(cart_serializer.data)


class RemoveCartItemView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, item_id):
        cart, created = Cart.objects.get_or_create(user=request.user)

        try:
            item = CartItem.objects.get(id=item_id, cart=cart)
        except CartItem.DoesNotExist:
            return Response(
                {'detail': 'Item no encontrado en tu carrito.'},
                status=status.HTTP_404_NOT_FOUND
            )

        item.delete()

        cart_serializer = CartSerializer(cart)
        return Response(cart_serializer.data)


class ClearCartView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        cart, created = Cart.objects.get_or_create(user=request.user)
        cart.items.all().delete()

        return Response(
            {'detail': 'Carrito vaciado correctamente.'},
            status=status.HTTP_200_OK
        )
