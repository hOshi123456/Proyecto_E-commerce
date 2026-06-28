from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

from catalog.models import Product


class Resena(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='resenas'
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='resenas'
    )

    rating = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(5),
        ]
    )

    comment = models.TextField(
        blank=True,
        default=''
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )

    class Meta:
        verbose_name = 'Reseña'
        verbose_name_plural = 'Reseñas'
        ordering = ['-created_at']

        constraints = [
            models.UniqueConstraint(
                fields=['user', 'product'],
                name='unique_resena_user_product'
            )
        ]

    def __str__(self):
        return (
            f'{self.user.username} - '
            f'{self.product.name} - '
            f'{self.rating}/5'
        )