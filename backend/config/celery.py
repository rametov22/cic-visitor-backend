import os

from django.conf import settings

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery(settings.APP_NAME)
app.conf.broker_url = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"
app.conf.result_backend = f"redis://{settings.REDIS_HOST}:{settings.REDIS_PORT}/0"
app.conf.timezone = settings.TIME_ZONE
app.conf.task_track_started = True
app.conf.task_soft_time_limit = 3 * 60 * 60
app.conf.task_time_limit = 3 * 60 * 60 + 60
app.conf.task_default_queue = "celery"
app.conf.accept_content = ["application/json"]
app.conf.task_serializer = "json"
app.conf.result_accept_content = ["application/json"]
app.conf.result_serializer = "json"
app.conf.broker_connection_retry_on_startup = True
app.conf.broker_connection_max_retries = None
app.conf.broker_connection_retry = True
app.conf.broker_connection_timeout = 4.0
app.conf.broker_heartbeat = 10
app.conf.beat_schedule_filename = "/tmp/celerybeat-schedule"
app.conf.beat_max_loop_interval = 60
app.autodiscover_tasks()
