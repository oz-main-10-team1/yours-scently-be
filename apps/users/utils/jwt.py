from rest_framework_simplejwt.tokens import RefreshToken

from apps.users.models import User


# 토큰 생성
def generate_jwt_tokens_for_user(user: User) -> dict[str, str]:
    refresh = RefreshToken.for_user(user)
    return {
        "access_token": str(refresh.access_token),
        "refresh_token": str(refresh),
    }
