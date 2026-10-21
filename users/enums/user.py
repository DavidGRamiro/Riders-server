from django.db.models.enums import TextChoices


class CarnetChoices(TextChoices):
    AM = "AM", "Carnet básico (14)"
    A1 = (
        "A1",
        "Carnet 125 (16)",
    )
    A2 = (
        "A2",
        "Carnet 35kw (18)",
    )
    A = (
        "A",
        "Carnet máximo (A2 + 2 años)",
    )
