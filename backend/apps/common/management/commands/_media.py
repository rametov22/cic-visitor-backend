from collections.abc import Iterator
from pathlib import PurePosixPath

from django.core.files.storage import Storage

STATIC_PREFIX = "static/"


def iter_storage_files(storage: Storage, prefix: str = "") -> Iterator[str]:
    directories, files = storage.listdir(prefix)
    for filename in files:
        yield str(PurePosixPath(prefix, filename))
    for directory in directories:
        child_prefix = str(PurePosixPath(prefix, directory))
        yield from iter_storage_files(storage, child_prefix)
