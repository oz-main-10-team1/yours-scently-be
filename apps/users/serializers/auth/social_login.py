from rest_framework import serializers


class SocialLoginSerializer(serializers.Serializer):
    code = serializers.CharField(help_text="인가 코드", error_messages={"required": "code는 필수입니다."})
    state = serializers.CharField(required=False, help_text="네이버 로그인 요청 시 함께 보낸 state 값")
