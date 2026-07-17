from django.apps import apps
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from django.db.models import CharField, FileField, TextField


class Command(BaseCommand):
    help = "Replace an old media base URL in text fields with the current one."

    def add_arguments(self, parser):
        parser.add_argument("--from", dest="old_base", required=True)
        parser.add_argument("--to", dest="new_base", default="")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, *args, **options):
        old_base = options["old_base"].rstrip("/") + "/"
        new_base = (
            options["new_base"].rstrip("/") if options["new_base"] else default_storage.url("").rstrip("/")
        ) + "/"
        if old_base == new_base:
            self.stdout.write(self.style.SUCCESS(f"Media base is unchanged ({new_base})."))
            return

        objects_changed = 0
        fields_changed = 0
        for model in apps.get_models():
            field_names = [
                field.name
                for field in model._meta.get_fields()
                if isinstance(field, (CharField, TextField)) and not isinstance(field, FileField)
            ]
            if not field_names:
                continue
            queryset = model._base_manager.all().only("pk", *field_names)
            for instance in queryset.iterator(chunk_size=500):
                dirty_fields = []
                for field_name in field_names:
                    value = getattr(instance, field_name, None)
                    if value and old_base in value:
                        setattr(
                            instance,
                            field_name,
                            value.replace(old_base, new_base),
                        )
                        dirty_fields.append(field_name)
                if dirty_fields:
                    objects_changed += 1
                    fields_changed += len(dirty_fields)
                    if not options["dry_run"]:
                        instance.save(update_fields=dirty_fields)

        verb = "Would update" if options["dry_run"] else "Updated"
        self.stdout.write(self.style.SUCCESS(f"{verb} {fields_changed} fields across {objects_changed} objects."))
