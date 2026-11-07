from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

from users.enums.user import CarnetChoices


# Create your models here.
class User(AbstractUser):
    direccion = models.CharField(blank=True, null=True, max_length=255)
    telf = models.IntegerField(blank=True, null=True)
    carnet = models.CharField(choices=CarnetChoices, blank=True, null=True, max_length=2)
    is_online = models.BooleanField(default=False)
    groups = models.ManyToManyField(
        Group,
        related_name="custom_user_groups",
        blank=True,
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name="custom_user_permissions",
        blank=True,
    )

    class Meta:
        db_table = "user"
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["id"]
