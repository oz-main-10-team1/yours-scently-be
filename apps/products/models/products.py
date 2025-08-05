from django.db import models
from django.contrib.postgres.fields import ArrayField


class products(models.Model):
    CATEGORY_CHOICES = [
        ('perfume', '향수'),
        ('etc','기타')

    ]

