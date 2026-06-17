from django.contrib import admin
from .models import Order, OrderItem


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = [
        'variant',
        'product_name',
        'variant_size',
        'variant_color',
        'unit_price',
        'quantity',
        'subtotal',
    ]

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'total', 'created_at', 'paid_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'user__email']
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'order',
        'product_name',
        'variant_size',
        'variant_color',
        'unit_price',
        'quantity',
        'subtotal',

    ]
    search_fields = ['product_name', 'order__user__username']
