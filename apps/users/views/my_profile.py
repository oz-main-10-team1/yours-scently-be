from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import User
from apps.users.serializers.my_profile import MyProfileSerializer


class MyProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user  # 인증된 사용자
        serializer = MyProfileSerializer(user)
        return Response(serializer.data)
