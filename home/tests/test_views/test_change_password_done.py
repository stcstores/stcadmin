import pytest
from django.urls import reverse
from requests_html import HTML


@pytest.fixture
def path():
    return "password_change_done"


@pytest.fixture
def url(path):
    return reverse(path)


@pytest.fixture
def get_page_text(valid_client, url):
    def _get_page_text():
        response = valid_client.get(url)
        return response.content.decode("utf8")

    return _get_page_text


@pytest.fixture
def page_text(get_page_text):
    return get_page_text()


@pytest.fixture
def html(page_text):
    return HTML(html=page_text)


@pytest.fixture
def get_html(get_page_text):
    def _get_html():
        return HTML(html=get_page_text())

    return _get_html


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
