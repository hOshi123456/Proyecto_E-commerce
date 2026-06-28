from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import Resena
from .permissions import IsOwnerOrReadOnly
from .serializers import ResenaSerializer


class ResenaViewSet(viewsets.ModelViewSet):
    serializer_class = ResenaSerializer

    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly,
    ]

    def get_queryset(self):
        queryset = Resena.objects.select_related(
            'user',
            'product'
        )

        product_id = self.request.query_params.get('product')

        if product_id:
            queryset = queryset.filter(
                product_id=product_id
            )

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)