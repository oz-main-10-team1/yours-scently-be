from django.urls import path

from apps.users.views.auth.email_auth import (
    SendEmailCodeView,
    VerifyEmailCodeView,
)
from apps.users.views.auth.phone_auth import (
    SendPhoneCodeAPIView,
    VerifyPhoneCodeAPIView,
)
from apps.users.views.auth.signup import (
    SignUpAPIView,
    SignupNicknameCheckAPIView,
)

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
]
