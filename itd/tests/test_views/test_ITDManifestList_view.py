import pytest

from itd import models, views


@pytest.fixture
def url():
    return "/itd/manifest_list/"


@pytest.fixture
def valid_get_response(valid_get_request, url):
    return valid_get_request(url)


@pytest.fixture
def valid_get_response_content(valid_get_response):
    return valid_get_response.content.decode("utf8")


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


def test_number_of_manifests_shown(url, group_logged_in_client, itd_manifest_factory):
    for i in range(views.ITDManifestList.MANIFESTS_TO_DISPLAY + 1):
        itd_manifest_factory.create(status=models.ITDManifest.CLOSED)
    response = group_logged_in_client.get(url)
    assert (
        len(response.context["manifests"]) == views.ITDManifestList.MANIFESTS_TO_DISPLAY
    )


def test_closed_manifest(url, group_logged_in_client, itd_manifest_factory):
    manifest = itd_manifest_factory.create(status=models.ITDManifest.CLOSED)
    response = group_logged_in_client.get(url)
    content = response.content.decode("utf8")
    assert manifest.status in content
    assert "disabled" not in content


def test_open_manifest(url, group_logged_in_client, itd_manifest_factory):
    manifest = itd_manifest_factory.create(status=models.ITDManifest.OPEN)
    response = group_logged_in_client.get(url)
    content = response.content.decode("utf8")
    assert manifest.status in content
    assert "disabled" in content


def test_generating_manifest(url, group_logged_in_client, itd_manifest_factory):
    manifest = itd_manifest_factory.create(status=models.ITDManifest.GENERATING)
    response = group_logged_in_client.get(url)
    content = response.content.decode("utf8")
    assert manifest.status in content
    assert "disabled" in content
    assert "img" in content


def test_error_manifest(url, group_logged_in_client, itd_manifest_factory):
    manifest = itd_manifest_factory.create(status=models.ITDManifest.ERROR)
    response = group_logged_in_client.get(url)
    content = response.content.decode("utf8")
    assert manifest.status in content
    assert "disabled" not in content
