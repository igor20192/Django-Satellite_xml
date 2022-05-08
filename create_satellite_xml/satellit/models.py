from pyexpat import model
from unicodedata import name
from django.db import models

# Create your models here.


class My_Sat_xml(models.Model):
    users_id = models.IntegerField()
    name = models.CharField(max_length=50)
    satellites = models.FileField()
