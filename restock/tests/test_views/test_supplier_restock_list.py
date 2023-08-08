from unittest import mock

import pytest
from django.urls import reverse


@pytest.fixture
def supplier(supplier_factory):
    return supplier_factory.create()


@pytest.fixture
def product(product_factory, supplier):
    return product_factory.create(supplier=supplier)


@pytest.fixture
def reorder(reorder_factory, product):
    return reorder_factory.create(closed=False, product=product)


@pytest.fixture
def mock_add_details_to_product():
    with mock.patch(
        "restock.views.add_details_to_product"
    ) as mock_add_details_to_product:
        yield mock_add_details_to_product


@pytest.fixture
def url(mock_add_details_to_product, supplier):
    return reverse("restock:supplier_restock_list", kwargs={"supplier_pk": supplier.pk})


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.mark.django_db
def test_uses_template(get_response):
    assert "restock/supplier_restock_list.html" in (
        t.name for t in get_response.templates
    )


@pytest.mark.django_db
def test_calls_add_details_to_product(
    mock_add_details_to_product, reorder, product, get_response
):
    mock_add_details_to_product.assert_called_once_with(product)


@pytest.mark.django_db
def test_suppliers_in_context(supplier, reorder, product, get_response):
    assert product in get_response.context["suppliers"][supplier]


@pytest.mark.django_db
def test_reorder_counts_in_context(reorder, product, get_response):
    assert get_response.context["reorder_counts"] == {product.id: reorder.count}


@pytest.mark.django_db
def test_comments_in_context(reorder, product, get_response):
    assert get_response.context["comments"] == {product.id: reorder.comment}
