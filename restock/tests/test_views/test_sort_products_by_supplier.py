from unittest import mock

import pytest

from restock import views


@pytest.fixture
def suppliers(supplier_factory):
    return supplier_factory.create_batch(3)


@pytest.fixture
def products(suppliers, product_factory):
    products = []
    for supplier in suppliers:
        products.extend(product_factory.build_batch(3, supplier=supplier))
    return products


@pytest.mark.django_db
@mock.patch("restock.views.add_details_to_product")
def test_sort_products_by_supplier(mock_add_details_to_product, suppliers, products):
    returned_value = views.sort_products_by_supplier(products)
    assert returned_value == {
        suppliers[0]: [products[0], products[1], products[2]],
        suppliers[1]: [products[3], products[4], products[5]],
        suppliers[2]: [products[6], products[7], products[8]],
    }


@pytest.mark.django_db
@mock.patch("restock.views.add_details_to_product")
def test_sort_products_by_supplier_sets_product_details(
    mock_add_details_to_product, products
):
    calls = (mock.call(product) for product in products)
    views.sort_products_by_supplier(products)
    mock_add_details_to_product.assert_has_calls(calls)
