import pytest
from django.urls import reverse

from inventory.views.product import ViewProduct


@pytest.fixture
def template_name():
    return "inventory/product_range/view_product.html"


def test_template_name_attribute(template_name):
    assert ViewProduct.template_name == template_name


@pytest.fixture
def product(product_factory):
    return product_factory.create()


@pytest.fixture
def url(product):
    return reverse("inventory:view_product", args=[product.pk])


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.mark.django_db
def test_uses_template(get_response, template_name):
    assert template_name in [t.name for t in get_response.templates]


@pytest.mark.django_db
def test_status_code(get_response):
    assert get_response.status_code == 200


@pytest.mark.django_db
def test_request_without_group(logged_in_client, url):
    assert logged_in_client.get(url).status_code == 403


def test_product_in_context(get_response, product):
    assert get_response.context["product"] == product


def test_product_range_in_context(get_response, product):
    assert get_response.context["product_range"] == product.product_range
