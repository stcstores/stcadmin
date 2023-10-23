from unittest import mock

import pytest
from django.shortcuts import reverse

from inventory.models import ProductRange


@pytest.fixture
def search_text():
    return "Text words"


@pytest.fixture
def reorder(reorder_factory, product):
    return reorder_factory.create(closed=False, product=product)


@pytest.fixture
def product(product_factory):
    return product_factory.create(sku="Text")


@pytest.fixture
def mock_add_details_to_product():
    with mock.patch(
        "restock.views.add_details_to_product"
    ) as mock_add_details_to_product:
        yield mock_add_details_to_product


@pytest.fixture
def url(mock_add_details_to_product):
    return reverse("restock:restock_results")


@pytest.fixture
def get_response(group_logged_in_client, url, search_text):
    return group_logged_in_client.get(url, {"product_search": search_text})


@pytest.mark.django_db
def test_uses_template(get_response):
    assert "restock/restock_list_display.html" in (
        t.name for t in get_response.templates
    )


@pytest.mark.django_db
def test_suppliers_in_context(product, get_response):
    assert get_response.context["suppliers"] == {product.supplier: [product]}


@pytest.mark.django_db
def test_calls_add_details_to_product(
    mock_add_details_to_product, product, get_response
):
    mock_add_details_to_product.assert_called_once_with(product)


@pytest.mark.django_db
def test_reorder_counts_in_context(product, reorder, get_response):
    assert get_response.context["reorder_counts"] == {product.id: reorder.count}


@pytest.mark.django_db
def test_comments_in_context(product, reorder, get_response):
    assert get_response.context["comments"] == {product.id: reorder.comment}


@pytest.mark.django_db
def test_product_matches_on_sku(
    product_factory, url, search_text, reorder, group_logged_in_client
):
    product = product_factory.create()
    response = group_logged_in_client.get(url, {"product_search": product.sku})
    assert response.context["suppliers"] == {product.supplier: [product]}


@pytest.mark.django_db
def test_product_matches_on_supplier_sku(
    product_factory, url, search_text, reorder, group_logged_in_client
):
    product = product_factory.create()
    response = group_logged_in_client.get(url, {"product_search": product.supplier_sku})
    assert response.context["suppliers"] == {product.supplier: [product]}


@pytest.mark.django_db
def test_product_matches_on_barcode(
    product_factory, url, search_text, reorder, group_logged_in_client
):
    product = product_factory.create()
    response = group_logged_in_client.get(url, {"product_search": product.barcode})
    assert response.context["suppliers"] == {product.supplier: [product]}


@pytest.mark.django_db
def test_does_not_return_incomplete_products(
    product_factory, url, search_text, reorder, group_logged_in_client
):
    product = product_factory.create(product_range__status=ProductRange.CREATING)
    response = group_logged_in_client.get(url, {"product_search": product.sku})
    assert response.context["suppliers"] == {}


@pytest.mark.django_db
def test_does_not_return_errored_products(
    product_factory, url, search_text, reorder, group_logged_in_client
):
    product = product_factory.create(product_range__status=ProductRange.ERROR)
    response = group_logged_in_client.get(url, {"product_search": product.sku})
    assert response.context["suppliers"] == {}


@pytest.mark.django_db
def test_does_not_return_archived_products(
    product_factory, url, search_text, reorder, group_logged_in_client
):
    product = product_factory.create(is_archived=True)
    response = group_logged_in_client.get(url, {"product_search": product.sku})
    assert response.context["suppliers"] == {}
