import pytest
from django.urls import reverse


@pytest.fixture
def order(fba_order_factory):
    return fba_order_factory.create(status_not_processed=True)


@pytest.fixture
def url(order):
    return reverse("fba:unstop_fba_order", args=[order.pk])


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


def test_status_code(get_response):
    assert get_response.status_code == 302


def test_request_without_group(logged_in_client, url):
    assert logged_in_client.get(url).status_code == 403


@pytest.mark.django_db
def test_sets_order_not_stopped(order, get_response):
    order.refresh_from_db()
    assert order.is_stopped is False


def test_redirect(get_response, order):
    assert reverse("fba:update_fba_order", args=[order.pk])
