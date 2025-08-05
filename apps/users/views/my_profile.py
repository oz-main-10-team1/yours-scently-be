from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import User
from apps.users.serializers.my_profile import (
    ChangePasswordSerializer,
    MyProfileSerializer,
    MyProfileUpdateSerializer,
    NicknameCheckSerializer,
)


class MyProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user  # 인증된 사용자
        serializer = MyProfileSerializer(user)
        return Response(serializer.data)


class MyProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        user = request.user
        serializer = MyProfileUpdateSerializer(user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# 내 정보 수정 - 비밀번호 변경
class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request):
        user = request.user
        serializer = ChangePasswordSerializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)

        new_password = serializer.validated_data["new_password"]
        user.set_password(new_password)
        user.save(update_fields=["password"])

        return Response(
            {
                "message": "비밀번호가 변경되었습니다.",
            },
            status=status.HTTP_200_OK,
        )


class NicknameDuplicateCheckView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        nickname = request.data.get("nickname")

        if not nickname:
            return Response({"detail": "nickname 필드는 필수입니다."}, status=400)

        if len(nickname) > 10:
            return Response({"nickname": ["닉네임은 10자 이하로 입력해주세요."]}, status=400)

        is_duplicate = User.objects.filter(nickname=nickname).exclude(id=request.user.id).exists()

        return Response({"is_duplicate": is_duplicate}, status=200)
