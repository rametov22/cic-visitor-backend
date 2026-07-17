from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.core.management import call_command

import pytest


def test_healthcheck(client):
    response = client.get("/healthcheck/")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.django_db
def test_news_categories(client):
    response = client.get("/ru/api/v1/iccu/static/categories/")
    assert response.status_code == 200


def test_media_manifest(capsys):
    default_storage.save("banners/example.txt", ContentFile(b"visitor"))
    call_command("media_info")
    output = capsys.readouterr().out
    assert '"object_count": 1' in output
    assert '"total_bytes": 7' in output
