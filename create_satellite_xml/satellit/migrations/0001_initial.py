# Generated by Django 4.0.4 on 2022-05-07 16:23

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='My_Satellites',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False)),
                ('satellite', models.FileField(upload_to='media/')),
            ],
        ),
    ]