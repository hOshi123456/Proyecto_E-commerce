from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from .serializers import RegisterSerializer, UserSerializer

from drf_spectacular.utils import (
    OpenApiExample,
    extend_schema,
    extend_schema_view,
)

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

@extend_schema_view(
    post=extend_schema(
        tags=['Usuarios'],
        summary='Registrar cliente',
        description='Crea un nuevo usuario con rol de cliente.',
        examples=[
            OpenApiExample(
                'Registro de cliente',
                value={
                    'username': 'cliente_demo',
                    'email': 'cliente.demo@gmail.com',
                    'first_name': 'María',
                    'last_name': 'González',
                    'phone': '0981123456',
                    'password': 'Cliente2026',
                    'password2': 'Cliente2026',
                },
                request_only=True,
            )
        ],
    )
)
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

class LoginView(TokenObtainPairView):

    @extend_schema(
        tags=['Usuarios'],
        summary='Iniciar sesión',
        description='Devuelve los tokens access y refresh.',
        examples=[
            OpenApiExample(
                'Inicio de sesión',
                value={
                    'username': 'cliente_demo',
                    'password': 'Cliente2026',
                },
                request_only=True,
            )
        ],
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class RefreshTokenView(TokenRefreshView):

    @extend_schema(
        tags=['Usuarios'],
        summary='Renovar token de acceso',
        description='Genera un access nuevo utilizando el refresh token.',
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=['Usuarios'],
        summary='Consultar usuario autenticado',
        responses=UserSerializer,
    )
    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
