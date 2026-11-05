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
    user_route_generate = models.ForeignKey(
        "UserGeneratedRoute",
        on_delete=models.CASCADE,
        related_name="users_ai_routes",
        blank=True,
        null=True,
    )

    class Meta:
        db_table = "user"
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["id"]


class UserGeneratedRoute(models.Model):
    id_fk_user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateField(auto_now_add=True)
    coords = models.CharField()
    waypoint = models.CharField()
    distance_km = models.FloatField()
    route_type = models.CharField()
    saved = models.BooleanField(default=False)

    class Meta:
        db_table = "user_generated_route"
        verbose_name = "User generated route"
        verbose_name_plural = "User generated routes"

    def __str__(self):
        return f"Ruta generada por {self.user.username}/{self.created_at}"
