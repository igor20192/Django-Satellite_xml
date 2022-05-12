import shutil
from unicodedata import name
from celery import shared_task
import os


@shared_task(name="rm_media")
def rm_media():
    shutil.rmtree("/home/igor/Django-Satellite_xml/create_satellite_xml/media")
    os.mkdir("/home/igor/Django-Satellite_xml/create_satellite_xml/media")
