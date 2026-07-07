from rest_framework import viewsets

from .models import Category, Product, ProductVariant
from .permissions import IsAdminOrReadOnly
from .serializers import (
    CategorySerializer,
    ProductSerializer,
    ProductVariantSerializer,
)
from drf_spectacular.utils import extend_schema


@extend_schema(tags=['Catálogo'])
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]

@extend_schema(tags=['Catálogo'])
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]

@extend_schema(tags=['Catálogo'])
class ProductVariantViewSet(viewsets.ModelViewSet):
    queryset = ProductVariant.objects.all()
    serializer_class = ProductVariantSerializer
    permission_classes = [IsAdminOrReadOnly]