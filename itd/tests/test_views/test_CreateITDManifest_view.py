from unittest.mock import patch

import pytest


@pytest.fixture
def url():
    return "/itd/create_manifest/"


@pytest.fixture
def mock_ITDManifest():
    with patch("itd.views.models.ITDManifest") as mock_ITDManifest:
        yield mock_ITDManifest


@pytest.fixture
def create_manifest_error(mock_ITDManifest):
    mock_ITDManifest.objects.create_manifest.side_effect = Exception


@pytest.fixture
def valid_get_response(mock_ITDManifest, valid_get_request, url):
    return valid_get_request(url)


def test_logged_out_get_method(url, logged_in_client):
    response = logged_in_client.get(url)
    assert response.status_code == 403


def test_logged_out_get(client, url):
    response = client.get(url)
    assert response.status_code == 302


def test_logged_in_group_get(valid_get_response):
    assert valid_get_response.status_code == 200


def test_logged_in_post(url, logged_in_client):
    response = logged_in_client.post(url)
    assert response.status_code == 403


def test_logged_out_post(client, url):
    response = client.post(url)
    assert response.status_code == 302


def test_logged_in_group_post(group_logged_in_client, url):
    response = group_logged_in_client.post(url)
    assert response.status_code == 405


def test_valid_request_response(valid_get_response):
    assert valid_get_response.content.decode("utf8") == "done"
    assert valid_get_response.status_code == 200


def test_request_creates_manifest(mock_ITDManifest, valid_get_response):
    mock_ITDManifest.objects.create_manifest.assert_called_once()


def test_request_error_response(create_manifest_error, valid_get_response):
    assert valid_get_response.status_code == 500
