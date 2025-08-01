# conftest.py (프로젝트 루트나 앱 디렉토리에 위치)
import os
import pytest
from django.conf import settings

# Pytest가 Django 설정을 로드하기 전에 실행됩니다.
def pytest_configure():
    # 환경 변수가 설정되지 않은 경우에만 설정
    os.environ.setdefault('DJANGO_SECRET_KEY', 'your_dummy_secret_key_for_tests')
    os.environ.setdefault('DB_NAME', 'test_db_name')
    os.environ.setdefault('DB_USER', 'test_db_user')
    os.environ.setdefault('DB_PASSWORD', 'test_db_password')
    os.environ.setdefault('DB_HOST', 'localhost')
    os.environ.setdefault('DB_PORT', '5432')
    os.environ.setdefault('REDIS_HOST', 'localhost')
    os.environ.setdefault('REDIS_PORT', '6379')
    os.environ.setdefault('TWILIO_ACCOUNT_SID', 'ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
    os.environ.setdefault('TWILIO_AUTH_TOKEN', 'your_dummy_twilio_auth_token')
    os.environ.setdefault('TWILIO_PHONE_NUMBER', '+15005550000')
    os.environ.setdefault('TWILIO_VERIFY_SERVICE_SID', 'VAxxxxxxxxxxxxxxxxxxxxxxxxxxxxx')
    os.environ.setdefault('EMAIL_HOST_USER', 'test@example.com')
    os.environ.setdefault('EMAIL_HOST_PASSWORD', 'test_password')
    # ... 필요한 모든 변수에 대해 os.environ.setdefault() 사용

    # Django 테스트용 이메일 백엔드 설정 (필요한 경우)
    settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
    # 실제 이메일 전송 대신 메모리에 저장되어 테스트 가능