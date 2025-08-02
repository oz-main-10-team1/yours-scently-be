from django_redis import get_redis_connection  # type: ignore

from apps.users.utils.twilio_utils import normalize_phone_number

# 회원가입 용 redis 함수


# 이메일 인증 코드를 Redis에 저장. 시간은 5분
def store_signup_email_code(email: str, code: str) -> None:
    redis = get_redis_connection("default")
    redis.set(f"signup:email:{email}", code, ex=300)


# redis 에서 이메일 인증 코드 조회
def get_signup_email_code(email: str) -> str | None:
    redis = get_redis_connection("default")
    code = redis.get(f"signup:email:{email}")
    return code.decode("utf-8") if code else None


# 이메일 인증 성공 시 인증 완료 상태를 Redis에 저장, 유효시간은 1시간 으로 설정
def mark_signup_email_as_verified(email: str) -> None:
    redis = get_redis_connection("default")
    redis.set(f"signup:email:verified:{email}", "true", ex=3600)


# 이메일 인증 여부 확인
def is_signup_email_verified(email: str) -> bool:
    redis = get_redis_connection("default")
    return redis.get(f"signup:email:verified:{email}") == b"true"


# 인증 코드 삭제
def delete_signup_email_code(email: str) -> None:
    redis = get_redis_connection("default")
    redis.delete(f"signup:email:{email}")


# 휴대폰 인증 완료 표시 (기본 TTL 5분)
def mark_phone_verified(phone: str, ttl: int = 300) -> None:
    redis = get_redis_connection("default")
    redis.set(f"signup:phone:verified:{phone}", "true", ex=ttl)


def is_phone_verified(phone: str) -> bool:
    redis = get_redis_connection("default")
    normalized = normalize_phone_number(phone)
    return redis.get(f"signup:phone:verified:{normalized}") == b"true"


# 비밀번호 찾기용


# 이메일 인증 코드를 Redis에 저장. 시간은 5분
def store_reset_email_code(email: str, code: str) -> None:
    redis = get_redis_connection("default")
    redis.set(f"reset:email:{email}", code, ex=300)


# redis 에서 이메일 인증 코드 조회
def get_reset_email_code(email: str) -> str | None:
    redis = get_redis_connection("default")
    code = redis.get(f"reset:email:{email}")
    return code.decode("utf-8") if code else None


# 이메일 인증 성공 시 인증 완료 상태를 Redis에 저장, 유효시간은 1시간 으로 설정
def mark_reset_email_as_verified(email: str) -> None:
    redis = get_redis_connection("default")
    redis.set(f"reset:email:verified:{email}", "true", ex=3600)


# 이메일 인증 여부 확인
def is_reset_email_verified(email: str) -> bool:
    redis = get_redis_connection("default")
    return redis.get(f"reset:email:verified:{email}") == b"true"


# 인증 코드 삭제
def delete_reset_email_code(email: str) -> None:
    redis = get_redis_connection("default")
    redis.delete(f"reset:email:{email}")


# 이메일 찾기 위한 휴대폰 인증
# 휴대폰 인증 완료 표시 (기본 TTL 5분)
def mark_email_find_phone_as_verified(phone: str, ttl: int = 300) -> None:
    redis = get_redis_connection("default")
    redis.set(f"email_find:verified:{phone}", "true", ex=ttl)


# 휴대폰 인증 여부 확인
def is_email_find_phone_verified(phone: str) -> bool:
    redis = get_redis_connection("default")
    return redis.get(f"email_find:verified:{phone}") == b"true"
