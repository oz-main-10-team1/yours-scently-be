from django.urls import path

from apps.users.views.auth.email_auth import (
    SendEmailCodeView,
    VerifyEmailCodeView,
)
from apps.users.views.auth.email_login import EmailLoginView
from apps.users.views.auth.kakao_social_login import KakaoLoginAPIView
from apps.users.views.auth.naver_social_login import NaverLoginAPIView
from apps.users.views.auth.signup import (
    SignUpAPIView,
    SignupNicknameCheckAPIView,
)
from apps.users.views.find_account_views import (
    EmailFindView,
    PasswordChangeView,
    PasswordResetEmailSendView,
    PasswordResetVerifyCodeView,
)
from apps.users.views.fragrance.fragrance_preference import (
    FragrancePreferenceView,
)
from apps.users.views.my_page import MyPageView
from apps.users.views.my_profile import (
    ChangePasswordView,
    MyProfileUpdateView,
    MyProfileView,
    NicknameDuplicateCheckView,
)
from apps.users.views.withdrawal import WithdrawalAPIView

urlpatterns = [
    # 회원가입
    path("signup/", SignUpAPIView.as_view(), name="signup"),
    path("signup/nickname-check/", SignupNicknameCheckAPIView.as_view(), name="nickname-check"),
    # 이메일 인증
    path("signup/email/send-code/", SendEmailCodeView.as_view(), name="email-send-code"),
    path("signup/email/verify/", VerifyEmailCodeView.as_view(), name="email-verify"),
    # 로그인
    path("login/email/", EmailLoginView.as_view(), name="email-login"),
    path("login/kakao/", KakaoLoginAPIView.as_view(), name="kakao-login"),
    path("login/naver/", NaverLoginAPIView.as_view(), name="naver-login"),
    # 회원 탈퇴
    path("deactivate/", WithdrawalAPIView.as_view(), name="user-withdrawal"),
    # 내 정보 조회
    path("users/me/", MyProfileView.as_view(), name="my-profile"),
    # 내 정보 수정
    path("users/me/update/", MyProfileUpdateView.as_view(), name="my-profile-update"),
    # 내 정보 수정 - 비밀번호 변경
    path("users/me/update/password/", ChangePasswordView.as_view(), name="update-change-password"),
    # 내 정보 수정 - 닉네임 중복 확인
    path("users/me/check-nickname/", NicknameDuplicateCheckView.as_view(), name="update-check-nickname"),
    # 마이페이지 조회
    path("user/mypage/", MyPageView.as_view(), name="mypage"),
    # 계정 찾기
    path("account/find-email/", EmailFindView.as_view(), name="email-find"),
    path("account/send-reset-code/", PasswordResetEmailSendView.as_view(), name="send-reset-code"),
    path("account/verify-code/", PasswordResetVerifyCodeView.as_view(), name="verify-code"),
    path("account/change-password/", PasswordChangeView.as_view(), name="change-password"),
    # 사용자 취향
    path("fragrance-preference/", FragrancePreferenceView.as_view(), name="fragrance-preference"),
]
