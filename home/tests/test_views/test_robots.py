import pytest


@pytest.fixture
def url():
    return "/robots.txt"


@pytest.fixture
def response(client, url):
    return client.get(url)


@pytest.mark.django_db
def test_can_access_logged_out(logged_out_client, url):
    assert logged_out_client.get(url).status_code == 200


@pytest.mark.django_db
def test_cannot_post(valid_client, url):
    assert valid_client.post(url).status_code == 405


def test_content_type(response):
    assert response["Content-Type"] == "text/plain"


def test_uses_template(response):
    assert "home/robots.txt" in (t.name for t in response.templates)
