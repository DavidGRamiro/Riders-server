from django.db.models.enums import TextChoices


class RouteTypes(TextChoices):
    RELAXED = "relaxed"
    FAST = "fast"
    TOUR = "tour"
    CIRCULAR = "circular"
    VIEWS = "views"
