from django.db import models

class Perfume(models.Model):
    class IntensityChoices(models.TextChoices):
        LIGHT = 'light', 'Light'
        MEDIUM = 'medium', 'Medium'
        STRONG = 'strong', 'Strong'

    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=50)
    release_year = models.IntegerField()
    top_notes = models.JSONField(default=list)        # varchar[] → JSONField로 매핑
    middle_notes = models.JSONField(default=list)
    base_notes = models.JSONField(default=list)
    main_accords = models.JSONField(default=list)
    intensity = models.CharField(
        max_length=10,
        choices=IntensityChoices.choices
    )

    def __str__(self):
        return f"{self.brand} - {self.name}"