from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.shared.models import BaseModel


class User(BaseModel, AbstractUser):
    email = models.EmailField(unique=True)
    token_version = models.IntegerField(default=1)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["username"]

    class Meta:
        ordering = ["id"]
        verbose_name = "User"
