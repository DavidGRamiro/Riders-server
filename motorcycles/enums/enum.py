from django.db.models.enums import TextChoices


class MotorcycleTypeChoice(TextChoices):
    CUSTOM = 'custom'
    NAKED = 'naked'
    SPORT = 'sport'
    TOURING = 'touring'
    CAFE_RACER = 'cafe_racer'
    SCRAMBLER = 'scrambler'
    TRAIL = 'trail'
    SCOOTER = 'scooter'