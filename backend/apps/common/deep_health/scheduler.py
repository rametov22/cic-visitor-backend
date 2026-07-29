import logging

from celery.beat import PersistentScheduler

from .heartbeat import write_beat_heartbeat

logger = logging.getLogger(__name__)


class HeartbeatScheduler(PersistentScheduler):
    def tick(self, *args, **kwargs):
        result = super().tick(*args, **kwargs)
        try:
            write_beat_heartbeat()
        except Exception:
            logger.exception("deep-health: failed to write celery-beat heartbeat")
        return result
