from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class UsageHistory(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="usage_histories"
    )
    product = models.ForeignKey("product.Product", on_delete=models.PROTECT, related_name="usage_histories")
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.product} (Rating: {self.rating}){f' | Comment: {self.comment}' if self.comment else ''}"
