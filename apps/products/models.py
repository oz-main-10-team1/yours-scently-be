from django.db import models

class Perfume(models.Model):
    name = models.CharField(max_length=255)
    brand = models.CharField(max_length=255)
    price = models.PositiveIntegerField(help_text="가격 (원 단위)")
    image_url = models.URLField(max_length=500)
    description = models.TextField()
    release_date = models.DateField()

    gender = models.CharField(
        max_length=10, null=True, blank=True,
        choices=[('Men', 'Men'), ('Women', 'Women'), ('Unisex', 'Unisex')],
        help_text="성별 구분"
    )

    class Meta:
        ordering = ['-id']  # 무한 스크롤 대응
        verbose_name = '향수'
        verbose_name_plural = '향수들'
        app_label = 'products'  # 필요한 경우 넣기

    def __str__(self):
        return f"{self.name} ({self.brand})"
