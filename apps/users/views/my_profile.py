from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.users.models import User
from apps.users.serializers.my_profile import (
    ChangePasswordSerializer,
    ChangePhoneWithCodeSerializer,
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


# 내 정보 수정 - 닉네임 중복 확인
class NicknameDuplicateCheckView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = NicknameCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        nickname = serializer.validated_data["nickname"]
        is_duplicate = User.objects.filter(nickname=nickname).exclude(id=request.user.id).exists()

        return Response({"is_duplicate": is_duplicate}, status=status.HTTP_200_OK)


# 내 정보 수정 - 휴대폰 인증
class ChangePhoneWithCodeAPIView(APIView):
    """
    사용자가 새 휴대폰 번호와 인증번호를 입력하면,
    인증번호가 일치할 경우 해당 번호로 사용자 정보를 즉시 업데이트합니다.
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePhoneWithCodeSerializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        serializer.save()
        return Response({"message": "휴대폰 번호가 성공적으로 변경되었습니다."}, status=status.HTTP_200_OK)
