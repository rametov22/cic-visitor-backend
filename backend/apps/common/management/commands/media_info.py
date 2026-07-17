import json

from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand

from ._media import STATIC_PREFIX, iter_storage_files


class Command(BaseCommand):
    help = "Print a JSON manifest for the configured media storage."

    def add_arguments(self, parser):
        parser.add_argument("--include-static", action="store_true")

    def handle(self, *args, **options):
        keys = [
            key
            for key in iter_storage_files(default_storage)
            if options["include_static"] or not key.startswith(STATIC_PREFIX)
        ]
        manifest = {
            "media_base_url": default_storage.url("").rstrip("/") + "/",
            "object_count": len(keys),
            "total_bytes": sum(default_storage.size(key) for key in keys),
        }
        self.stdout.write(json.dumps(manifest, ensure_ascii=False, indent=2))
