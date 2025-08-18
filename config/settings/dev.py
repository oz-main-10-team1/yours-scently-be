from config.settings.base import *

DEBUG = False

allowed_hosts_raw = os.getenv("DJANGO_ALLOWED_HOSTS", "")
if not allowed_hosts_raw:
    raise ValueError("환경변수 DJANGO_ALLOWED_HOSTS가 설정되지 않았습니다.")
ALLOWED_HOSTS: list[str] = allowed_hosts_raw.split()

# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

INTERNAL_IPS = [
    "127.0.0.1",
]

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "https://yours-scently-fe.vercel.app",
    "https://www.yours-scently.store",
    "https://yours-scently.store",
]
