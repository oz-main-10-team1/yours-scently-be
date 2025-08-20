from rest_framework import serializers


class ProductLikeResponseSerializer(serializers.Serializer):
    liked = serializers.BooleanField()
