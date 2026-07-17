import sys
import tarfile

from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Read a gzipped media tar from stdin and restore it to current storage."

    def add_arguments(self, parser):
        parser.add_argument("--skip-existing", action="store_true")

    def handle(self, *args, **options):
        loaded = 0
        skipped = 0
        with tarfile.open(fileobj=sys.stdin.buffer, mode="r|gz") as archive:
            for member in archive:
                if not member.isfile():
                    continue
                if member.name.startswith("/") or ".." in member.name.split("/"):
                    raise CommandError(f"Unsafe path in media archive: {member.name}")
                if default_storage.exists(member.name):
                    if options["skip_existing"]:
                        skipped += 1
                        continue
                    default_storage.delete(member.name)
                source = archive.extractfile(member)
                if source is None:
                    continue
                default_storage.save(member.name, ContentFile(source.read()))
                loaded += 1
                if loaded % 250 == 0:
                    self.stderr.write(f"  ...{loaded} files")

        self.stderr.write(self.style.SUCCESS(f"Loaded {loaded} files, skipped {skipped}."))
