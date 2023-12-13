import pytest
from django.urls import reverse


@pytest.fixture
def path():
    return "password_change_done"


@pytest.fixture
def url(path):
    return reverse(path)


@pytest.mark.django_db
def test_can_access_logged_out(logged_out_client, url):
    assert logged_out_client.get(url).status_code == 302


@pytest.mark.django_db
def test_can_post(valid_client, url):
    assert valid_client.post(url).status_code == 302


@pytest.mark.django_db
def test_logs_out_on_get_request(url, valid_client):
    valid_client.get(url)
    assert "_auth_user_id" not in valid_client.session


@pytest.mark.django_db
def test_logs_out_on_post_request(url, valid_client):
    valid_client.post(url)
    assert "_auth_user_id" not in valid_client.session


@pytest.mark.django_db
def test_redirects_get_request(url, valid_client):
    response = valid_client.get(url)
    assert response.status_code == 302
    expected_redirect = reverse("home:login_user")
    assert response["Location"] == expected_redirect


@pytest.mark.django_db
def test_redirects_post_request(url, valid_client):
    response = valid_client.post(url)
    assert response.status_code == 302
    expected_redirect = reverse("home:login_user")
    assert response["Location"] == expected_redirect
