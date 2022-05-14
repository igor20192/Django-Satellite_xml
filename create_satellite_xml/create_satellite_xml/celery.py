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
