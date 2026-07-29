import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from datetime import UTC, datetime
from uuid import uuid4

from django.conf import settings
from django.db import connections

from redis import Redis
from redis.backoff import NoBackoff
from redis.retry import Retry

from config.celery import app as celery_app

from .heartbeat import read_beat_heartbeat

STATUS_PRIORITY = {"ok": 0, "degraded": 1, "down": 2}
BEAT_OK_AGE_SECONDS = 150
BEAT_DEGRADED_AGE_SECONDS = 600


def _service_result(service, status, detail, started_at=None):
    result = {
        "service": service,
        "status": status,
        "detail": detail,
    }
    if started_at is not None:
        result["latency_ms"] = round((time.perf_counter() - started_at) * 1000, 2)
    return result


def _check_backend():
    return _service_result("backend", "ok", "application is responsive")


def _check_database():
    service = "db"
    started_at = time.perf_counter()
    connection = connections["default"]
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            if cursor.fetchone() != (1,):
                raise ValueError("unexpected database response")
    except Exception:
        return _service_result(service, "down", "query failed", started_at)
    finally:
        connection.close()
    return _service_result(service, "ok", "query passed", started_at)


def _check_redis():
    service = "redis"
    started_at = time.perf_counter()
    key = f"deep-health:{uuid4().hex}"
    client = Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=1,
        socket_connect_timeout=settings.DEEP_HEALTH_CLIENT_TIMEOUT_SECONDS,
        socket_timeout=settings.DEEP_HEALTH_CLIENT_TIMEOUT_SECONDS,
        retry=Retry(NoBackoff(), 0),
    )
    try:
        if not client.ping():
            raise ValueError("PING failed")
        client.set(key, "ok", ex=5)
        if client.get(key) != b"ok":
            raise ValueError("read/write failed")
    except Exception:
        return _service_result(service, "down", "PING or read/write failed", started_at)
    finally:
        client.close()
    return _service_result(service, "ok", "PING and read/write passed", started_at)


def _check_celery():
    service = "celery"
    started_at = time.perf_counter()
    try:
        replies = celery_app.control.inspect(timeout=settings.DEEP_HEALTH_CLIENT_TIMEOUT_SECONDS).ping() or {}
    except Exception:
        return _service_result(service, "down", "worker ping failed", started_at)
    if not replies:
        return _service_result(service, "down", "no workers online", started_at)
    return _service_result(service, "ok", f"{len(replies)} worker(s) online", started_at)


def _check_celery_beat():
    service = "celery-beat"
    try:
        last_heartbeat = read_beat_heartbeat()
    except Exception:
        return _service_result(service, "down", "heartbeat read failed")
    if last_heartbeat is None:
        return _service_result(service, "down", "no heartbeat")

    age = max(0, round(time.time() - float(last_heartbeat)))
    if age <= BEAT_OK_AGE_SECONDS:
        return _service_result(service, "ok", f"heartbeat {age}s ago")
    if age <= BEAT_DEGRADED_AGE_SECONDS:
        return _service_result(service, "degraded", f"heartbeat {age}s ago")
    return _service_result(service, "down", f"stale heartbeat {age}s")


CHECKS = (
    ("backend", _check_backend),
    ("db", _check_database),
    ("redis", _check_redis),
    ("celery", _check_celery),
    ("celery-beat", _check_celery_beat),
)


def _collect_services():
    deadline = time.monotonic() + settings.DEEP_HEALTH_DEADLINE_SECONDS
    executor = ThreadPoolExecutor(max_workers=len(CHECKS), thread_name_prefix="deep-health")
    futures = [(service, executor.submit(check)) for service, check in CHECKS]
    services = []

    for service, future in futures:
        remaining = max(0, deadline - time.monotonic())
        try:
            services.append(future.result(timeout=remaining))
        except TimeoutError:
            services.append(_service_result(service, "down", "shared deadline exceeded"))
        except Exception:
            services.append(_service_result(service, "down", "healthcheck failed"))

    executor.shutdown(wait=False, cancel_futures=True)
    return services


def build_deep_health_report():
    services = _collect_services()
    status = max(services, key=lambda item: STATUS_PRIORITY[item["status"]])["status"]
    return {
        "status": status,
        "generated_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        "services": services,
    }
