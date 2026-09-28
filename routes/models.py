from django.db import models

from users.models import User


class Route(models.Model):
    id_fk_usuario = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, blank=True, db_column="id_fk_usuario", related_name="user_route")
    title = models.CharField(max_length=255, null=False, blank=False, db_comment="Title of route")
    is_ai_generated = models.BooleanField(default=False, db_comment="True if is AI generated")
    path_data = models.TextField(null=False, blank=False, db_comment="Path of route")
    distance_km = models.FloatField(null=False, blank=False, db_comment="Distance km of route")

    class Meta:
        db_table = "routes"
        verbose_name = "Route"
        verbose_name_plural = "Routes"

    def __str__(self) -> str:
        return f"{self.title} - {self.distance_km} km"