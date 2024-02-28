import pytest
from django.urls import reverse


@pytest.fixture
def order(fba_order_factory):
    return fba_order_factory.create(status_not_processed=True)


@pytest.fixture
def get_params(order):
    return {"order_id": order.pk}


@pytest.fixture
def url():
    return reverse("fba:priortise_fba_order")


@pytest.fixture
def get_response(group_logged_in_client, url, get_params):
    return group_logged_in_client.get(url, get_params)


def test_status_code(get_response):
    assert get_response.status_code == 200


def test_request_without_group(logged_in_client, url, get_params):
    assert logged_in_client.get(url, get_params).status_code == 403


def test_content(get_response):
    assert get_response.content == b"ok"


@pytest.mark.django_db
def test_prioritised_order(order, get_response):
    order.refresh_from_db()
    assert order.is_prioritised() is True
