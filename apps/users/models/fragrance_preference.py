from django.conf import settings
from django.db import models


class FragrancePreference(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="fragrance_preference")

    preferred_top_notes = models.ManyToManyField(
        "product.Note", related_name="preferred_top_notes", limit_choices_to={"type": "top"}
    )

    preferred_middle_notes = models.ManyToManyField(
        "product.Note", related_name="preferred_middle_notes", limit_choices_to={"type": "middle"}
    )

    preferred_base_notes = models.ManyToManyField(
        "product.Note", related_name="preferred_base_notes", limit_choices_to={"type": "base"}
    )

    preferred_accords = models.ManyToManyField("product.Accord", related_name="preferred_accords")

    class IntensityChoices(models.TextChoices):
        PARFUM = "parfum", "Parfum (20~30%, 8~12시간)"
        EAU_DE_PARFUM = "eau_de_parfum", "Eau de Parfum (15~20%, 6~8시간)"
        EAU_DE_TOILETTE = "eau_de_toilette", "Eau de Toilette (5~15%, 4~6시간)"
        EAU_DE_COLOGNE = "eau_de_cologne", "Eau de Cologne (2~5%, 2~4시간)"
        EAU_FRAICHE = "eau_fraiche", "Eau Fraîche (1~3%, 1~2시간)"

    intensity = models.CharField(max_length=20, choices=IntensityChoices.choices)

    preferences = models.JSONField(default=dict)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.nickname}'s fragrance preference"
