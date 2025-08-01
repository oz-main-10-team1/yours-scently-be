from django.urls import path

from apps.users.views.auth.email_auth import (
    SendEmailCodeView,
    VerifyEmailCodeView,
)
from apps.users.views.auth.email_login import EmailLoginView
from apps.users.views.auth.kakao_social_login import KakaoLoginAPIView
from apps.users.views.auth.naver_social_login import NaverLoginAPIView
from apps.users.views.auth.phone_auth import (
    SendPhoneCodeAPIView,
    VerifyPhoneCodeAPIView,
)
from apps.users.views.auth.signup import (
    SignUpAPIView,
    SignupNicknameCheckAPIView,
)
from apps.users.views.my_profile import MyProfileView
from apps.users.views.withdrawal import WithdrawalAPIView

urlpatterns = [
    # 회원가입
    path("signup/", SignUpAPIView.as_view(), name="signup"),
    path("signup/nickname-check/", SignupNicknameCheckAPIView.as_view(), name="nickname-check"),
    # 이메일 인증
    path("signup/email/send-code/", SendEmailCodeView.as_view(), name="email-send-code"),
    path("signup/email/verify/", VerifyEmailCodeView.as_view(), name="email-verify"),
    # 휴대폰인증
    path("signup/phone/send-code/", SendPhoneCodeAPIView.as_view(), name="phone-send-code"),
    path("signup/phone/verify/", VerifyPhoneCodeAPIView.as_view(), name="phone-verify"),
    # 로그인
    path("login/email/", EmailLoginView.as_view(), name="email-login"),
    path("login/kakao/", KakaoLoginAPIView.as_view(), name="kakao-login"),
    path("login/naver/", NaverLoginAPIView.as_view(), name="naver-login"),
    # 회원 탈퇴
    path("deactivate/", WithdrawalAPIView.as_view(), name="user-withdrawal"),
    # 내정보 조회
    path("mypage/", MyProfileView.as_view(), name="my-profile"),
]
