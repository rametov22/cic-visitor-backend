import os

if os.environ.get("DJANGO_SETTINGS_MODULE", "").endswith(".test"):
    os.environ.setdefault("ENVIRONMENT", "test")

from .base import *
from .third_party import *

if ENVIRONMENT == "dev":
    from .dev import *
