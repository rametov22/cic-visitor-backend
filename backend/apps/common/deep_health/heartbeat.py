import time

from django.core.cache import cache

BEAT_HEARTBEAT_KEY = "deep-health:celery-beat:heartbeat"
BEAT_HEARTBEAT_TTL_SECONDS = 15 * 60


def write_beat_heartbeat():
    cache.set(BEAT_HEARTBEAT_KEY, time.time(), timeout=BEAT_HEARTBEAT_TTL_SECONDS)


def read_beat_heartbeat():
    return cache.get(BEAT_HEARTBEAT_KEY)
