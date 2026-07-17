import io
import sys
import tarfile
import time

from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand

from ._media import STATIC_PREFIX, iter_storage_files


class Command(BaseCommand):
    help = "Stream a gzipped tar of all media files to stdout."

    def add_arguments(self, parser):
        parser.add_argument("--prefix", default="")
        parser.add_argument("--include-static", action="store_true")

    def handle(self, *args, **options):
        prefix = options["prefix"].strip("/")
        include_static = options["include_static"]
        count = 0
        total = 0

        with tarfile.open(fileobj=sys.stdout.buffer, mode="w|gz") as archive:
            for key in iter_storage_files(default_storage, prefix):
                if not include_static and key.startswith(STATIC_PREFIX):
                    continue
                with default_storage.open(key, "rb") as source:
                    data = source.read()
                info = tarfile.TarInfo(name=key)
                info.size = len(data)
                info.mtime = int(time.time())
                archive.addfile(info, io.BytesIO(data))
                count += 1
                total += len(data)
                if count % 250 == 0:
                    self.stderr.write(f"  ...{count} files ({total / 1024 / 1024:.1f} MB)")

        self.stderr.write(self.style.SUCCESS(f"Dumped {count} files, {total / 1024 / 1024:.1f} MB."))
