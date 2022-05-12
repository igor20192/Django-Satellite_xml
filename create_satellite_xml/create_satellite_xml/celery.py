from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# from django_celery_beat.models import CrontabSchedule, PeriodicTask
import pytz

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "create_satellite_xml.settings")
app = Celery("create_satellite_xml")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.conf.timezone = "Europe/Kiev"
app.autodiscover_tasks()
"""schedule, _ = CrontabSchedule.objects.get_or_create(
    minute="55",
    hour="9",
    day_of_week="*",
    day_of_month="*",
    month_of_year="*",
    timezone=pytz.timezone("Europe/Kiev"),
)

PeriodicTask.objects.create(
    crontab=schedule,
    name="rm_media",
    task="task.tasks.rm_media",
)"""
