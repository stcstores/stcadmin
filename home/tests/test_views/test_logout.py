import pytest
from django.urls import reverse


@pytest.fixture
def path():
    return "home:logout_user"


@pytest.fixture
def url(path):
    return reverse(path)


@pytest.mark.django_db
def test_can_post(client, url):
    assert client.post(url).status_code == 302


@pytest.mark.django_db
def test_logs_out(url, valid_client):
    valid_client.post(url)
    assert "_auth_user_id" not in valid_client.session


@pytest.mark.django_db
def test_login_redirect(url, user, valid_client):
    response = valid_client.post(url)
    assert response.status_code == 302
    assert response["Location"] == reverse("home:login_user")
