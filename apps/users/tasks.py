import logging
from datetime import date

from celery import shared_task  # type: ignore
from django.conf import settings
from django.core.mail import send_mail

from apps.users.models import User, Withdrawal

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=30)
def send_verification_email_task(self, email: str, code: str) -> None:
    try:
        send_mail(
            subject="[Yours, Scently] 이메일 인증 코드입니다.",
            message=f"인증 코드는 {code} 입니다.",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )
    except Exception as exception:
        logger.warning(f"[재시도] 이메일 전송 실패: {email}/사유: {exception}")
        raise self.retry(exc=exception)


# 14일이 지난 계정들 매일 정오에 자동으로 삭제
@shared_task
def delete_expired_withdrawn_users():
    today = date.today()
    expired_withdrawals = Withdrawal.objects.filter(due_date__lte=today).select_related("user")

    user_ids_to_delete = []

    for w in expired_withdrawals:
        logger.info(f"[Celery] 탈퇴 유예 기간이 만료된 사용자 삭제: {w.user.email} (ID: {w.user.id})")
        user_ids_to_delete.append(w.user.id)

    if user_ids_to_delete:
        deleted_count, _ = User.objects.filter(id__in=user_ids_to_delete).delete()
        logger.info(f"[Celery] 탈퇴 유예 기간이 지난 사용자 {deleted_count}명 삭제")

    else:
        logger.info("[Celery] 삭제할 탈퇴 유예 기간이 지난 사용자가 없습니다.")
