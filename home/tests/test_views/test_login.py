import pytest
from django.urls import reverse
from requests_html import HTML


@pytest.fixture
def path():
    return "home:login_user"


@pytest.fixture
def url(path):
    return reverse(path)


@pytest.fixture
def get_page_text(logged_out_client, url):
    def _get_page_text():
        response = logged_out_client.get(url)
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
def test_can_access_logged_in(valid_client, url):
    assert valid_client.get(url).status_code == 200


@pytest.mark.django_db
def test_can_post(logged_out_client, url):
    assert logged_out_client.post(url).status_code == 200


def test_contains_form(url, html):
    assert html.find(f'form[action="{url}"][method="post"]')


def test_contains_username_input(html):
    assert html.find('input[name="username"]')


def test_contains_password_input(html):
    assert html.find('input[name="password"][type="password"]')


@pytest.mark.django_db
def test_can_login(url, user, test_password, client):
    client.post(url, {"username": user.username, "password": test_password})
    assert client.session["_auth_user_id"]
