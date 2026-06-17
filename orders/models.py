from decimal import Decimal

from django.conf import settings
from django.db import models

from catalog.models import ProductVariant


class Order(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_PAID = 'paid'
    STATUS_CANCELLED = 'cancelled'
    STATUS_SHIPPED = 'shipped'
    STATUS_DELIVERED = 'delivered'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pendiente'),
        (STATUS_PAID, 'Pagado'),
        (STATUS_CANCELLED, 'Cancelado'),
        (STATUS_SHIPPED, 'Enviado'),
        (STATUS_DELIVERED, 'Entregado'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders'
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING
    )

    cupon = models.ForeignKey(
        'cupones.Cupon',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders'
    )

    cupon_code = models.CharField(
        max_length=50,
        blank=True,
        default=''
    )

    discount_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )

    paid_at = models.DateTimeField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = 'Orden'
        verbose_name_plural = 'Órdenes'
        ordering = ['-created_at']

    def __str__(self):
        return f'Orden #{self.id} - {self.user.username}'

    @property
    def subtotal(self):
        return sum(
            (item.subtotal for item in self.items.all()),
            Decimal('0.00')
        )

    @property
    def total(self):
        final_total = self.subtotal - self.discount_amount

        return max(
            final_total,
            Decimal('0.00')
        )


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items'
    )

    variant = models.ForeignKey(
        ProductVariant,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='order_items'
    )

    product_name = models.CharField(
        max_length=150
    )

    variant_size = models.CharField(
        max_length=20
    )

    variant_color = models.CharField(
        max_length=50
    )

    unit_price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    quantity = models.PositiveIntegerField()

    class Meta:
        verbose_name = 'Item de orden'
        verbose_name_plural = 'Items de órdenes'

    def __str__(self):
        return f'{self.product_name} x {self.quantity}'

    @property
    def subtotal(self):
        return self.unit_price * self.quantity