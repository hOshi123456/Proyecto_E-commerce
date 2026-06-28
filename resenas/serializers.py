from rest_framework import serializers

from orders.models import Order, OrderItem

from .models import Resena


class ResenaSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(
        source='user.username',
        read_only=True
    )

    product_name = serializers.CharField(
        source='product.name',
        read_only=True
    )

    class Meta:
        model = Resena

        fields = [
            'id',
            'user',
            'user_name',
            'product',
            'product_name',
            'rating',
            'comment',
            'created_at',
            'updated_at',
        ]

        read_only_fields = [
            'id',
            'user',
            'user_name',
            'product_name',
            'created_at',
            'updated_at',
        ]

    def validate(self, attrs):
        request = self.context['request']
        user = request.user

        product = attrs.get(
            'product',
            self.instance.product if self.instance else None
        )

        compro_producto = OrderItem.objects.filter(
            order__user=user,
            order__status=Order.STATUS_PAID,
            variant__product=product
        ).exists()

        if not compro_producto:
            raise serializers.ValidationError({
                'product': (
                    'Solo podés reseñar productos que hayas '
                    'comprado y pagado.'
                )
            })

        resenas_existentes = Resena.objects.filter(
            user=user,
            product=product
        )

        if self.instance:
            resenas_existentes = resenas_existentes.exclude(
                id=self.instance.id
            )

        if resenas_existentes.exists():
            raise serializers.ValidationError({
                'product': (
                    'Ya publicaste una reseña para este producto.'
                )
            })

        return attrs