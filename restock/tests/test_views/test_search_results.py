from unittest import mock

import pytest
from django.shortcuts import reverse

from inventory.models import ProductRange


@pytest.fixture
def search_text():
    return "Text"


@pytest.fixture
def reorder(reorder_factory, product):
    return reorder_factory.create(closed=False, product=product)


@pytest.fixture
def product(product_factory, search_text):
    return product_factory.create(sku=search_text)


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
    product_factory, url, search_text, group_logged_in_client
):
    product = product_factory.create(sku=search_text)
    response = group_logged_in_client.get(url, {"product_search": search_text})
    assert response.context["suppliers"] == {product.supplier: [product]}


@pytest.mark.django_db
def test_product_matches_on_supplier_sku(
    product_factory, url, search_text, group_logged_in_client
):
    product = product_factory.create(supplier_sku=search_text)
    response = group_logged_in_client.get(url, {"product_search": search_text})
    assert response.context["suppliers"] == {product.supplier: [product]}


@pytest.mark.django_db
def test_product_matches_on_barcode(
    product_factory, url, search_text, group_logged_in_client
):
    product = product_factory.create(barcode=search_text)
    response = group_logged_in_client.get(url, {"product_search": search_text})
    assert response.context["suppliers"] == {product.supplier: [product]}


@pytest.mark.django_db
def test_does_not_return_incomplete_products(
    product_factory, url, search_text, group_logged_in_client
):
    product_factory.create(sku=search_text, product_range__status=ProductRange.CREATING)
    response = group_logged_in_client.get(url, {"product_search": search_text})
    assert response.context["suppliers"] == {}


@pytest.mark.django_db
def test_does_not_return_errored_products(
    product_factory, url, search_text, group_logged_in_client
):
    product_factory.create(sku=search_text, product_range__status=ProductRange.ERROR)
    response = group_logged_in_client.get(url, {"product_search": search_text})
    assert response.context["suppliers"] == {}


@pytest.mark.django_db
def test_does_not_return_EOL_products(
    product_factory, url, search_text, group_logged_in_client
):
    product_factory.create(sku=search_text, is_end_of_line=True)
    response = group_logged_in_client.get(url, {"product_search": search_text})
    assert response.context["suppliers"] == {}
