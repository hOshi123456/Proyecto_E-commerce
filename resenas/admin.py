from django.contrib import admin

from .models import Resena


@admin.register(Resena)
class ResenaAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user',
        'product',
        'rating',
        'created_at',
    ]

    search_fields = [
        'user__username',
        'product__name',
        'comment',
    ]

    list_filter = [
        'rating',
        'created_at',
    ]