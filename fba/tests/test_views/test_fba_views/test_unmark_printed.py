import pytest
from django.urls import reverse


@pytest.fixture
def order(fba_order_factory):
    return fba_order_factory.create(status_printed=True)


@pytest.fixture
def url(order):
    return reverse("fba:unmark_printed", args=[order.pk])


@pytest.fixture
def next_url():
    return "next_url"


@pytest.fixture
def get_response(group_logged_in_client, url, next_url):
    return group_logged_in_client.get(url, {"next": next_url})


def test_status_code(get_response):
    assert get_response.status_code == 302


def test_request_without_group(logged_in_client, url):
    assert logged_in_client.get(url).status_code == 403


@pytest.mark.django_db
def test_sets_order_not_printed(order, get_response):
    order.refresh_from_db()
    assert order.printed is False


def test_redirect(get_response, next_url):
    assert get_response["location"] == next_url
