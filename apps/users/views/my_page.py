from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models.user import User
from apps.users.serializers.my_page import MyPageSerializer


class MyPageView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = User.objects.prefetch_related("perfumes__main_accords").get(pk=request.user.pk)
        serializer = MyPageSerializer(user)
        return Response(
            {"code": 200, "message": "마이페이지 정보 조회 성공", "data": serializer.data}, status=status.HTTP_200_OK
        )
