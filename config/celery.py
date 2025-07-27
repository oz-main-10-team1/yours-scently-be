import os

from celery import Celery  # type: ignore
from celery.schedules import crontab  # type: ignore

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.local")

app = Celery("oz_externship")

app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
