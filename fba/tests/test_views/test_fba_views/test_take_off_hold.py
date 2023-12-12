import pytest
from django.urls import reverse


@pytest.fixture
def order(fba_order_factory):
    return fba_order_factory.create(status_on_hold=True)


@pytest.fixture
def url():
    return reverse("fba:take_off_hold")


@pytest.fixture
def params(order):
    return {"order_id": order.pk}


@pytest.fixture
def get_response(group_logged_in_client, url, params):
    return group_logged_in_client.get(url, params)


def test_status_code(get_response):
    assert get_response.status_code == 200


def test_request_without_group(logged_in_client, url):
    assert logged_in_client.get(url).status_code == 403


def test_response_text(get_response):
    assert get_response.content == b"ok"


def test_takes_order_off_hold(get_response, order):
    order.refresh_from_db()
    assert order.on_hold is False
