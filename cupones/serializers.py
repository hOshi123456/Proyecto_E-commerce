from decimal import Decimal

from rest_framework import serializers

from .models import Cupon


class CuponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cupon
        fields = [
            'id',
            'code',
            'discount_type',
            'discount_value',
            'minimum_order_amount',
            'valid_from',
            'valid_until',
            'usage_limit',
            'times_used',
            'is_active',
            'created_at',
            'updated_at',
        ]

        read_only_fields = [
            'id',
            'times_used',
            'created_at',
            'updated_at',
        ]

    def validate_code(self, value):
        return value.strip().upper()

    def validate(self, attrs):
        instance = self.instance

        discount_type = attrs.get(
            'discount_type',
            getattr(instance, 'discount_type', None)
        )

        discount_value = attrs.get(
            'discount_value',
            getattr(instance, 'discount_value', None)
        )

        valid_from = attrs.get(
            'valid_from',
            getattr(instance, 'valid_from', None)
        )

        valid_until = attrs.get(
            'valid_until',
            getattr(instance, 'valid_until', None)
        )

        usage_limit = attrs.get(
            'usage_limit',
            getattr(instance, 'usage_limit', None)
        )

        if (
            discount_type == Cupon.TYPE_PERCENTAGE
            and discount_value is not None
            and discount_value > Decimal('100.00')
        ):
            raise serializers.ValidationError({
                'discount_value': (
                    'El porcentaje no puede superar el 100%.'
                )
            })

        if (
            valid_until
            and valid_from
            and valid_until <= valid_from
        ):
            raise serializers.ValidationError({
                'valid_until': (
                    'La fecha final debe ser posterior '
                    'a la fecha inicial.'
                )
            })

        if usage_limit is not None and usage_limit < 1:
            raise serializers.ValidationError({
                'usage_limit': (
                    'El límite de usos debe ser mayor que cero.'
                )
            })

        return attrs


class CuponValidationSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=50)

    subtotal = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal('0.01')
    )

class CuponValidationResponseSerializer(serializers.Serializer):
    valid = serializers.BooleanField()
    code = serializers.CharField()

    subtotal = serializers.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    discount_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    final_total = serializers.DecimalField(
        max_digits=12,
        decimal_places=2
    )