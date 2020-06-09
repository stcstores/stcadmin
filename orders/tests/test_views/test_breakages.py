import pytest
from django.utils.html import escape
from pytest_django.asserts import assertTemplateUsed


@pytest.fixture
def url():
    return "/orders/breakages/"


@pytest.fixture
def valid_get_response(valid_get_request, url):
    return valid_get_request(url)


@pytest.fixture
def valid_get_response_content(valid_get_response):
    return valid_get_response.content.decode("utf8")


@pytest.fixture
def breakage(breakage_factory):
    return breakage_factory.create()


def test_logged_in_get(url, logged_in_client):
    response = logged_in_client.get(url)
    assert response.status_code == 403


def test_logged_out_get(client, url):
    response = client.get(url)
    assert response.status_code == 302


def test_logged_in_group_get(group_logged_in_client, url):
    response = group_logged_in_client.get(url)
    assert response.status_code == 200


def test_logged_in_post(url, logged_in_client):
    response = logged_in_client.post(url)
    assert response.status_code == 403


def test_logged_out_post(client, url):
    response = client.post(url)
    assert response.status_code == 302


def test_logged_in_group_post(group_logged_in_client, url):
    response = group_logged_in_client.post(url)
    assert response.status_code == 405


def test_uses_template(valid_get_response):
    assert assertTemplateUsed(valid_get_response, "orders/breakages.html") is not False


@pytest.mark.django_db
def test_breakage_order_id_in_content(breakage, valid_get_response_content):
    assert breakage.order_id in valid_get_response_content


@pytest.mark.django_db
def test_breakage_sku_in_content(breakage, valid_get_response_content):
    assert breakage.product_sku in valid_get_response_content


@pytest.mark.django_db
def test_breakage_note_in_content(breakage, valid_get_response_content):
    assert escape(breakage.note) in valid_get_response_content
