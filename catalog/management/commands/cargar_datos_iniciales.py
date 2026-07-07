import json
from datetime import timedelta
from decimal import Decimal

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from catalog.models import Category, Product, ProductVariant
from cupones.models import Cupon


User = get_user_model()


class Command(BaseCommand):
    help = 'Carga clientes, categorías, productos, variantes y cupones.'

    @transaction.atomic
    def handle(self, *args, **options):
        file_path = (
            settings.BASE_DIR
            / 'data'
            / 'datos_iniciales.json'
        )

        if not file_path.exists():
            raise CommandError(
                f'No se encontró el archivo: {file_path}'
            )

        try:
            with file_path.open(
                mode='r',
                encoding='utf-8'
            ) as file:
                data = json.load(file)
        except json.JSONDecodeError as error:
            raise CommandError(
                f'El archivo JSON no es válido: {error}'
            )

        self.crear_cliente(data.get('cliente'))
        self.crear_categorias(data.get('categorias', []))
        self.crear_productos(data.get('productos', []))
        self.crear_cupones(data.get('cupones', []))

        self.stdout.write(
            self.style.SUCCESS(
                'Datos iniciales cargados correctamente.'
            )
        )

    def crear_cliente(self, cliente_data):
        if not cliente_data:
            return

        user, created = User.objects.update_or_create(
            username=cliente_data['username'],
            defaults={
                'email': cliente_data['email'],
                'first_name': cliente_data.get(
                    'first_name',
                    ''
                ),
                'last_name': cliente_data.get(
                    'last_name',
                    ''
                ),
                'phone': cliente_data.get(
                    'phone',
                    ''
                ),
                'role': cliente_data.get(
                    'role',
                    'client'
                ),
                'is_active': True,
                'is_staff': False,
            }
        )

        user.set_password(cliente_data['password'])
        user.save(update_fields=['password'])

        action = 'creado' if created else 'actualizado'

        self.stdout.write(
            f'Cliente {user.username}: {action}.'
        )

    def crear_categorias(self, categorias):
        for categoria_data in categorias:
            categoria, created = (
                Category.objects.update_or_create(
                    name=categoria_data['name'],
                    defaults={
                        'description': categoria_data.get(
                            'description',
                            ''
                        ),
                        'is_active': categoria_data.get(
                            'is_active',
                            True
                        ),
                    }
                )
            )

            action = 'creada' if created else 'actualizada'

            self.stdout.write(
                f'Categoría {categoria.name}: {action}.'
            )

    def crear_productos(self, productos):
        for producto_data in productos:
            try:
                categoria = Category.objects.get(
                    name=producto_data['category']
                )
            except Category.DoesNotExist:
                raise CommandError(
                    'No existe la categoría '
                    f'{producto_data["category"]}.'
                )

            producto, created = (
                Product.objects.update_or_create(
                    name=producto_data['name'],
                    defaults={
                        'category': categoria,
                        'description': producto_data.get(
                            'description',
                            ''
                        ),
                        'base_price': Decimal(
                            producto_data['base_price']
                        ),
                        'image_url': producto_data.get(
                            'image_url',
                            ''
                        ),
                        'is_active': producto_data.get(
                            'is_active',
                            True
                        ),
                    }
                )
            )

            action = 'creado' if created else 'actualizado'

            self.stdout.write(
                f'Producto {producto.name}: {action}.'
            )

            self.crear_variantes(
                producto,
                producto_data.get('variants', [])
            )

    def crear_variantes(self, producto, variantes):
        for variante_data in variantes:
            variante, created = (
                ProductVariant.objects.update_or_create(
                    product=producto,
                    size=variante_data['size'],
                    color=variante_data['color'],
                    defaults={
                        'stock': variante_data.get(
                            'stock',
                            0
                        ),
                        'extra_price': Decimal(
                            variante_data.get(
                                'extra_price',
                                '0.00'
                            )
                        ),
                    }
                )
            )

            action = 'creada' if created else 'actualizada'

            self.stdout.write(
                f'  Variante {variante}: {action}.'
            )

    def crear_cupones(self, cupones):
        now = timezone.now()

        for cupon_data in cupones:
            valid_days = cupon_data.get(
                'valid_days',
                30
            )

            valid_until = (
                now + timedelta(days=valid_days)
                if valid_days
                else None
            )

            cupon, created = Cupon.objects.update_or_create(
                code=cupon_data['code'].strip().upper(),
                defaults={
                    'discount_type': (
                        cupon_data['discount_type']
                    ),
                    'discount_value': Decimal(
                        cupon_data['discount_value']
                    ),
                    'minimum_order_amount': Decimal(
                        cupon_data.get(
                            'minimum_order_amount',
                            '0.00'
                        )
                    ),
                    'valid_from': now,
                    'valid_until': valid_until,
                    'usage_limit': cupon_data.get(
                        'usage_limit'
                    ),
                    'is_active': cupon_data.get(
                        'is_active',
                        True
                    ),
                }
            )

            action = 'creado' if created else 'actualizado'

            self.stdout.write(
                f'Cupón {cupon.code}: {action}.'
            )