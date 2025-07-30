from django.db import models

from apps.users.models.user import User


class SearchLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    keyword = models.CharField(max_length=100)
    result_count = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.id} - {self.keyword} ({self.created_at})"
