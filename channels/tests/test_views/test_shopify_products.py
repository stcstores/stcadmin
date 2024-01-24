import pytest
from django.urls import reverse

from channels.forms import ProductSearchForm
from channels.views import ShopifyProducts
from inventory.models import ProductRange


@pytest.fixture
def template():
    return "channels/shopify/search_page.html"


def test_template_name_attribute(template):
    assert ShopifyProducts.template_name == template


def test_model_attribute():
    assert ShopifyProducts.model == ProductRange


def test_paginate_by_attribute():
    assert ShopifyProducts.paginate_by == 50


def test_orphans_attribute():
    assert ShopifyProducts.orphans == 3


def test_form_class_attribute():
    assert ShopifyProducts.form_class == ProductSearchForm


@pytest.fixture
def url():
    return reverse("channels:shopify_products")


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


def test_uses_template(template, get_response):
    assert template in [t.name for t in get_response.templates]


def test_status_code(get_response):
    assert get_response.status_code == 200


def test_request_without_group(logged_in_client, url):
    assert logged_in_client.get(url).status_code == 403


def test_form_in_context(get_response):
    assert isinstance(get_response.context["form"], ProductSearchForm)


def test_object_list_in_context(get_response):
    assert "object_list" in get_response.context


def test_invalid_form_submission(group_logged_in_client, url):
    response = group_logged_in_client.get(url, {"listed": "hello"})
    assert response.status_code == 200
    assert len(response.context["object_list"]) == 0
    assert response.context["form"].is_valid() is False


def test_object_list_not_empty(group_logged_in_client, url, product_factory):
    product = product_factory.create()
    response = group_logged_in_client.get(url)
    assert product.product_range in response.context["object_list"]


def test_filters(product_factory, group_logged_in_client, url):
    expected_product = product_factory.create()
    unexpected_product = product_factory.create()
    params = {"search_term": expected_product.sku}
    response = group_logged_in_client.get(url, params)
    assert response.context["object_list"].contains(expected_product.product_range)
    assert (
        response.context["object_list"].contains(unexpected_product.product_range)
        is False
    )
