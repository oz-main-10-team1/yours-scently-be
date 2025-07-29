from datetime import date, timedelta

from django.conf import settings
from django.db import models


def default_due_date():
    return date.today() + timedelta(days=14)


class Withdrawal(models.Model):
    class Reason(models.TextChoices):
        NOT_ACCURATE = "NOT_ACCURATE", "추천이 정확하지 않음"
        NOT_SATISFIED = "NOT_SATISFIED", "불만족"
        ETC = "ETC", "기타"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="withdrawal",
    )
    reason = models.CharField(max_length=20, choices=Reason.choices)
    reason_detail = models.TextField()
    due_date = models.DateField(default=default_due_date)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "withdrawals"

    def __str__(self) -> str:
        return f"{self.user.email} - {self.get_reason_display()}"  # type: ignore
