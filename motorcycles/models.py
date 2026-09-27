from django.db import models

from motorcycles.enums.enum import MotorcycleTypeChoice
from users.models import User


class Motorcycle(models.Model):
    id_fk_usuario = models.ForeignKey(User, db_column='id_fk_usuario', on_delete=models.CASCADE, db_comment="Usuario asociado", related_name="motorcycles")
    brand = models.CharField(max_length=100, null=False, blank=False, db_comment="Marca de moto")
    model = models.CharField(max_length=100, null=False, blank=False, db_comment="Modelo de moto")
    type = models.CharField(choices=MotorcycleTypeChoice, null=False, blank=False,db_comment="Tipo de moto")
    engine_cc = models.CharField(max_length=6, null=False, blank=False, db_comment="Cilindrada")
    year = models.IntegerField(null=False, blank=False, db_comment="Año de moto")
    kilometers = models.IntegerField(null=False, blank=False, db_comment="Kilometrage")
    color = models.CharField(max_length=20, db_comment="Color")

    def __str__(self):
        return f"{self.brand} - {self.type} - {self.engine_cc}"


