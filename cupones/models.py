from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone


class Cupon(models.Model):
    TYPE_PERCENTAGE = 'percentage'
    TYPE_FIXED = 'fixed'

    DISCOUNT_TYPE_CHOICES = [
        (TYPE_PERCENTAGE, 'Porcentaje'),
        (TYPE_FIXED, 'Monto fijo'),
    ]

    code = models.CharField(
        max_length=50,
        unique=True
    )

    discount_type = models.CharField(
        max_length=20,
        choices=DISCOUNT_TYPE_CHOICES
    )

    discount_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )

    minimum_order_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    valid_from = models.DateTimeField(
        default=timezone.now
    )

    valid_until = models.DateTimeField(
        blank=True,
        null=True
    )

    usage_limit = models.PositiveIntegerField(
        blank=True,
        null=True
    )

    times_used = models.PositiveIntegerField(
        default=0
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = 'Cupón'
        verbose_name_plural = 'Cupones'
        ordering = ['-created_at']

    def __str__(self):
        return self.code

    def clean(self):
        errors = {}

        if (
            self.discount_type == self.TYPE_PERCENTAGE
            and self.discount_value > Decimal('100.00')
        ):
            errors['discount_value'] = (
                'El descuento porcentual no puede superar el 100%.'
            )

        if (
            self.valid_until
            and self.valid_from
            and self.valid_until <= self.valid_from
        ):
            errors['valid_until'] = (
                'La fecha de vencimiento debe ser posterior '
                'a la fecha de inicio.'
            )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.code = self.code.strip().upper()
        super().save(*args, **kwargs)

    def is_valid(self):
        now = timezone.now()

        if not self.is_active:
            return False

        if self.valid_from and now < self.valid_from:
            return False

        if self.valid_until and now > self.valid_until:
            return False

        if (
            self.usage_limit is not None
            and self.times_used >= self.usage_limit
        ):
            return False

        return True

    def calculate_discount(self, subtotal):
        subtotal = Decimal(subtotal)

        if subtotal < self.minimum_order_amount:
            return Decimal('0.00')

        if self.discount_type == self.TYPE_PERCENTAGE:
            discount = (
                subtotal * self.discount_value
            ) / Decimal('100.00')
        else:
            discount = self.discount_value

        discount = min(discount, subtotal)

        return discount.quantize(Decimal('0.01'))
