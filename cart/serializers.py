from rest_framework import serializers

from catalog.models import ProductVariant
from catalog.serializers import ProductVariantSerializer
from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    variant_detail = ProductVariantSerializer(source='variant', read_only=True)
    subtotal = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = CartItem
        fields = [
            'id',
            'variant',
            'variant_detail',
            'quantity',
            'subtotal',
        ]
        read_only_fields = ['id', 'variant_detail', 'subtotal']


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = Cart
        fields = [
            'id',
            'user',
            'items',
            'total',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'user', 'items', 'total', 'created_at', 'updated_at']


class AddCartItemSerializer(serializers.Serializer):
    variant = serializers.PrimaryKeyRelatedField(
        queryset=ProductVariant.objects.all()
    )
    quantity = serializers.IntegerField(min_value=1)

    def validate(self, data):
        variant = data['variant']
        quantity = data['quantity']

        if variant.stock <= 0:
            raise serializers.ValidationError('Esta variante no tiene stock disponible.')

        if quantity > variant.stock:
            raise serializers.ValidationError(
                f'Solo hay {variant.stock} unidades disponibles.'
            )

        return data


class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=1)