from django.conf import settings
from django.db import models


class UsageHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="usage_histories")
    product = models.ForeignKey("product.Product", on_delete=models.CASCADE, related_name="usage_histories")
    rating = models.IntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.product} (Rating: {self.rating}){f' | Comment: {self.comment}' if self.comment else ''}"
