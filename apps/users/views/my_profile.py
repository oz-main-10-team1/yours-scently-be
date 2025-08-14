from drf_spectacular.utils import OpenApiResponse, extend_schema, inline_serializer
from rest_framework import serializers, status
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

    @extend_schema(
        summary="마이프로필 조회",
        tags=["MyProfile"],
        responses={
            200: MyProfileSerializer,
        },
    )
    def get(self, request):
        user = request.user  # 인증된 사용자
        serializer = MyProfileSerializer(user)
        return Response(serializer.data)


class MyProfileUpdateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="마이프로필 수정",
        tags=["MyProfile"],
        request=MyProfileUpdateSerializer,  # 요청 바디 스키마
        responses={
            200: MyProfileSerializer,  # 성공 시 응답 스키마(수정된 프로필)
            400: OpenApiResponse(description="검증 실패 또는 잘못된 요청 데이터"),
            401: OpenApiResponse(description="인증 실패"),
        },
    )
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

    @extend_schema(
        summary="비밀번호 변경",
        tags=["MyProfile"],
        request=ChangePasswordSerializer,
        responses={
            200: inline_serializer(
                name="ChangePasswordOK",
                fields={"message": serializers.CharField()},
            ),
            400: OpenApiResponse(description="검증 실패(현재 비밀번호 불일치 등)"),
            401: OpenApiResponse(description="인증 실패"),
        },
    )
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

    @extend_schema(
        summary="닉네임 중복 확인",
        tags=["MyProfile"],
        request=NicknameCheckSerializer,  # 요청 바디: {"nickname": "값"}
        responses={
            200: inline_serializer(
                name="NicknameDuplicateCheckOK",
                fields={
                    "is_duplicate": serializers.BooleanField(help_text="이미 사용 중이면 true"),
                },
            ),
            400: OpenApiResponse(description="검증 실패(잘못된 닉네임 형식 등)"),
            401: OpenApiResponse(description="인증 실패"),
        },
    )
    def post(self, request):
        serializer = NicknameCheckSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        nickname = serializer.validated_data["nickname"]
        is_duplicate = User.objects.filter(nickname=nickname).exclude(id=request.user.id).exists()

        return Response({"is_duplicate": is_duplicate}, status=status.HTTP_200_OK)
