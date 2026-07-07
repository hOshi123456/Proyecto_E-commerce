from rest_framework import status, viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Cupon
from .serializers import (
    CuponSerializer,
    CuponValidationSerializer,
    CuponValidationResponseSerializer,
)
from drf_spectacular.utils import extend_schema

@extend_schema(tags=['Cupones'])
class CuponViewSet(viewsets.ModelViewSet):
    queryset = Cupon.objects.all()
    serializer_class = CuponSerializer
    permission_classes = [IsAdminUser]


@extend_schema(tags=['Cupones'])
class CuponValidationView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Cupones'],
        summary='Validar cupón',
        description=(
            'Comprueba si un cupón está activo y calcula '
            'el descuento según el subtotal.'
        ),
        request=CuponValidationSerializer,
        responses={
            200: CuponValidationResponseSerializer,
        },
    )
    def post(self, request):
        serializer = CuponValidationSerializer(
            data=request.data
        )
        serializer.is_valid(raise_exception=True)

        code = serializer.validated_data['code'].strip().upper()
        subtotal = serializer.validated_data['subtotal']

        try:
            cupon = Cupon.objects.get(code=code)
        except Cupon.DoesNotExist:
            return Response(
                {'detail': 'El cupón ingresado no existe.'},
                status=status.HTTP_404_NOT_FOUND
            )

        if not cupon.is_valid():
            return Response(
                {
                    'detail': (
                        'El cupón está vencido, inactivo '
                        'o alcanzó su límite de usos.'
                    )
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        if subtotal < cupon.minimum_order_amount:
            return Response(
                {
                    'detail': (
                        'El subtotal no alcanza el monto mínimo '
                        'requerido para este cupón.'
                    ),
                    'minimum_order_amount': (
                        cupon.minimum_order_amount
                    ),
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        discount = cupon.calculate_discount(subtotal)
        final_total = subtotal - discount

        return Response({
            'valid': True,
            'code': cupon.code,
            'subtotal': subtotal,
            'discount_amount': discount,
            'final_total': final_total,
        })