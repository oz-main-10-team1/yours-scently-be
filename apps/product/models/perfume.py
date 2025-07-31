from django.db import models

from apps.product.models import Accord, Note


class Perfume(models.Model):
    class IntensityChoices(models.TextChoices):
        LIGHT = "light", "Light"
        MEDIUM = "medium", "Medium"
        STRONG = "strong", "Strong"

    name = models.CharField(max_length=100)
    brand = models.CharField(max_length=50)
    release_year = models.IntegerField()

    top_notes = models.ManyToManyField(Note, related_name="top_perfumes", limit_choices_to={"type": "top"})
    middle_notes = models.ManyToManyField(Note, related_name="middle_perfumes", limit_choices_to={"type": "middle"})
    base_notes = models.ManyToManyField(Note, related_name="base_perfumes", limit_choices_to={"type": "base"})

    main_accords = models.ManyToManyField(Accord, related_name="perfumes")

    intensity = models.CharField(max_length=10, choices=IntensityChoices.choices)

    def __str__(self):
        return f"{self.brand} - {self.name}"
