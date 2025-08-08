from rest_framework import serializers
from apps.users.models.user import User
from apps.product.models.perfume import Perfume

class MyPerfumeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Perfume
        fields = [
            'id',           # perfume_id
            'name',
            'brand',
            'main_accords',
            'intensity',
        ]

class MyPageSerializer(serializers.ModelSerializer):
    # ✅ 실제 User 모델에 연결된 필드명 사용 (예: perfumes)
    perfumes = MyPerfumeSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'nickname',
            'phone_number',
            'birth_date',
            'gender',
            'created_at',
            'perfumes',
        ]
