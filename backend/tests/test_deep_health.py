from unittest.mock import patch

from django.test import override_settings

import pytest

from common.deep_health.checks import _check_celery_beat, build_deep_health_report


@override_settings(DEEP_HEALTH_API_KEY="monitoring-secret")
@patch("common.deep_health.views.build_deep_health_report")
def test_deep_health_rejects_missing_key_without_running_checks(build_report, client):
    response = client.get("/deep-health/")

    assert response.status_code == 401
    assert response.json() == {"detail": "Unauthorized"}
    assert response.headers["Cache-Control"] == "no-store"
    build_report.assert_not_called()


@override_settings(DEEP_HEALTH_API_KEY="monitoring-secret")
@patch("common.deep_health.views.build_deep_health_report")
def test_deep_health_rejects_wrong_key_without_running_checks(build_report, client):
    response = client.get("/deep-health/", headers={"X-API-Key": "wrong-secret"})

    assert response.status_code == 401
    build_report.assert_not_called()


@override_settings(DEEP_HEALTH_API_KEY="monitoring-secret")
@patch("common.deep_health.views.build_deep_health_report")
def test_deep_health_returns_http_200_even_when_service_is_down(build_report, client):
    build_report.return_value = {
        "status": "down",
        "generated_at": "2026-07-29T10:00:00Z",
        "services": [{"service": "celery", "status": "down", "detail": "no workers online"}],
    }

    response = client.get("/deep-health/", headers={"X-API-Key": "monitoring-secret"})

    assert response.status_code == 200
    assert response.json() == build_report.return_value
    assert response.headers["Cache-Control"] == "no-store"


@override_settings(DEEP_HEALTH_API_KEY="")
@patch("common.deep_health.views.build_deep_health_report")
def test_deep_health_is_disabled_when_server_key_is_empty(build_report, client):
    response = client.get("/deep-health/", headers={"X-API-Key": "any-key"})

    assert response.status_code == 401
    build_report.assert_not_called()


def test_deep_health_allows_only_get(client):
    response = client.post("/deep-health/")

    assert response.status_code == 405


@override_settings(DEEP_HEALTH_DEADLINE_SECONDS=1.5)
def test_deep_health_report_uses_worst_status_and_compose_service_names():
    checks = (
        ("backend", lambda: {"service": "backend", "status": "ok", "detail": "passed"}),
        ("db", lambda: {"service": "db", "status": "ok", "detail": "passed"}),
        ("redis", lambda: {"service": "redis", "status": "ok", "detail": "passed"}),
        ("celery", lambda: {"service": "celery", "status": "down", "detail": "failed"}),
        ("celery-beat", lambda: {"service": "celery-beat", "status": "degraded", "detail": "stale"}),
    )

    with patch("common.deep_health.checks.CHECKS", checks):
        report = build_deep_health_report()

    assert report["status"] == "down"
    assert report["generated_at"].endswith("Z")
    assert [item["service"] for item in report["services"]] == [
        "backend",
        "db",
        "redis",
        "celery",
        "celery-beat",
    ]


@pytest.mark.parametrize(
    ("heartbeat", "expected_status"),
    [
        (None, "down"),
        (950.0, "ok"),
        (700.0, "degraded"),
        (300.0, "down"),
    ],
)
@patch("common.deep_health.checks.time.time", return_value=1000.0)
def test_celery_beat_status_uses_shared_heartbeat(_current_time, heartbeat, expected_status):
    with patch("common.deep_health.checks.read_beat_heartbeat", return_value=heartbeat):
        result = _check_celery_beat()

    assert result["service"] == "celery-beat"
    assert result["status"] == expected_status
