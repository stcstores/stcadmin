import pytest
from django.urls import reverse

from fba.models import FBAOrder
from fba.views.fba import DeleteFBAOrder


def test_model_attribute():
    assert DeleteFBAOrder.model == FBAOrder


@pytest.fixture
def order(fba_order_factory):
    return fba_order_factory.create(status_ready=True)


@pytest.fixture
def fulfilled_order(fba_order_factory):
    return fba_order_factory.create(status_fulfilled=True)


@pytest.fixture
def url(order):
    return reverse("fba:delete_order", args=[order.pk])


@pytest.fixture
def fulfilled_url(fulfilled_order):
    return reverse("fba:delete_order", args=[fulfilled_order.pk])


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.fixture
def post_response(group_logged_in_client, url):
    return group_logged_in_client.post(url, {})


@pytest.mark.django_db
def test_uses_template(get_response):
    assert "fba/fbaorder_confirm_delete.html" in [
        t.name for t in get_response.templates
    ]


def test_status_code(get_response):
    assert get_response.status_code == 200


def test_get_without_group(logged_in_client, url):
    assert logged_in_client.get(url).status_code == 403


def test_post_without_group(logged_in_client, url):
    assert logged_in_client.post(url, {}).status_code == 403


def test_order_in_context(get_response, order):
    assert get_response.context["object"] == order


def test_deletes_order(post_response, order):
    assert FBAOrder.objects.filter(id=order.id).exists() is False


def test_redirects(post_response):
    assert post_response.status_code == 302
    assert post_response["Location"] == reverse("fba:order_list")


@pytest.mark.django_db
def test_does_not_delete_fulfilled_order(
    fulfilled_url, fulfilled_order, group_logged_in_client
):
    response = group_logged_in_client.post(fulfilled_url, {})
    assert response.status_code == 403
    assert FBAOrder.objects.filter(id=fulfilled_order.id).exists()
