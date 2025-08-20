from django.db import models


class Note(models.Model):
    class NoteType(models.TextChoices):
        TOP = "top", "Top"
        MIDDLE = "middle", "Middle"
        BASE = "base", "Base"

    name = models.CharField(max_length=50)
    type = models.CharField(max_length=10, choices=NoteType.choices)

    def __str__(self):
        return f"{self.get_type_display()} - {self.name}"
