from django.contrib.auth.models import User
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Creates a superuser."

    def handle(self, *args, **options):
        if not User.objects.filter(username="igor").exists():
            User.objects.create_superuser(username="igor", password="18452704xu")
        print("Superuser has been created.")
