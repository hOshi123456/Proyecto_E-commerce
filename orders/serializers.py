from rest_framework import serializers

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = OrderItem
        fields = [
            'id',
            'variant',
            'product_name',
            'variant_size',
            'variant_color',
            'unit_price',
            'quantity',
            'subtotal',
        ]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        read_only=True
    )

    class Meta:
        model = Order
        fields = [
            'id',
            'user',
            'status',
            'items',
            'total',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'user',
            'status',
            'items',
            'total',
            'created_at',
            'updated_at',
        ]