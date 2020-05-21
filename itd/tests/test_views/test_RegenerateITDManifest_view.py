from unittest.mock import patch

import pytest

from itd import models


@pytest.fixture
def url(manifest):
    return f"/itd/regenerate_manifest/{manifest.id}/"


@pytest.fixture
def mock_regenerate_async():
    with patch(
        "itd.views.models.ITDManifest.regenerate_async"
    ) as mock_regenerate_async:
        yield mock_regenerate_async


@pytest.fixture
def manifest(itd_manifest_factory):
    return itd_manifest_factory.create(status=models.ITDManifest.CLOSED)


@pytest.fixture
def valid_get_response(mock_regenerate_async, valid_get_request, url):
    return valid_get_request(url)


@pytest.mark.django_db
def test_logged_out_get_method(url, logged_in_client):
    response = logged_in_client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_logged_out_get(client, url):
    response = client.get(url)
    assert response.status_code == 302


@pytest.mark.django_db
def test_logged_in_group_get(valid_get_response):
    assert valid_get_response.status_code == 200


@pytest.mark.django_db
def test_logged_in_post(url, logged_in_client):
    response = logged_in_client.post(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_logged_out_post(client, url):
    response = client.post(url)
    assert response.status_code == 302


@pytest.mark.django_db
def test_logged_in_group_post(group_logged_in_client, url):
    response = group_logged_in_client.post(url)
    assert response.status_code == 405


@pytest.mark.django_db
def test_valid_request_response(valid_get_response):
    assert valid_get_response.content.decode("utf8") == "done"
    assert valid_get_response.status_code == 200


@pytest.mark.django_db
def test_request_creates_manifest(mock_regenerate_async, valid_get_response, manifest):
    manifest.regenerate_async.assert_called_once()
