from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Create and verify local static and media directories."

    def handle(self, *args, **options):
        settings.MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
        settings.STATIC_ROOT.mkdir(parents=True, exist_ok=True)
        self.stdout.write(self.style.SUCCESS("Filesystem storage is ready."))
