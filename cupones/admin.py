from django.contrib import admin

from .models import Cupon


@admin.register(Cupon)
class CuponAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'code',
        'discount_type',
        'discount_value',
        'minimum_order_amount',
        'times_used',
        'usage_limit',
        'is_active',
        'valid_from',
        'valid_until',
    ]

    search_fields = ['code']

    list_filter = [
        'discount_type',
        'is_active',
        'valid_from',
        'valid_until',
    ]

    readonly_fields = [
        'times_used',
        'created_at',
        'updated_at',
    ]
