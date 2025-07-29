from rest_framework import serializers
from .models import Perfume


class PerfumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perfume
        fields = ['id', 'name', 'brand', 'price', 'image_url', 'description', 'release_date']
