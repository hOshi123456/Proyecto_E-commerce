from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    ROLE_CLIENT = 'client'
    ROLE_ADMIN = 'admin'

    ROLE_CHOICES = [
        (ROLE_CLIENT, 'Cliente'),
        (ROLE_ADMIN, 'Administrador'),
    ]

    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default=ROLE_CLIENT
    )

    def __str__(self):
        return self.username