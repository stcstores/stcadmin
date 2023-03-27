from unittest import mock

import pytest
from django.urls import reverse


@pytest.fixture
def product_range(product_range_factory):
    return product_range_factory.create()


@pytest.fixture
def products(product_range, product_factory):
    return product_factory.create_batch(3, product_range=product_range)


@pytest.fixture
def url(product_range):
    return reverse("inventory:product_range", kwargs={"range_pk": product_range.pk})


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.fixture(autouse=True)
def mock_stock_manager():
    with mock.patch("inventory.views.productrange.StockManager") as mock_stock_manager:
        yield mock_stock_manager


@pytest.mark.django_db
def test_uses_template(get_response):
    assert "inventory/product_range/product_range.html" in (
        t.name for t in get_response.templates
    )


@pytest.mark.django_db
def test_product_range_in_context(product_range, get_response):
    assert get_response.context["product_range"] == product_range


@pytest.mark.django_db
def test_products_in_context(products, get_response):
    assert set(get_response.context["products"]) == set(products)


@pytest.mark.django_db
def test_products_exist_in_context(products, mock_stock_manager, get_response):
    products_exist = get_response.context["products_exist"]
    assert products_exist == mock_stock_manager.products_exist.return_value
    mock_stock_manager.products_exist.assert_called_once_with(
        *[product.sku for product in products]
    )


@pytest.mark.django_db
def test_ignores_errors_checking_products_exist(
    products, mock_stock_manager, group_logged_in_client, url
):
    mock_stock_manager.products_exist.side_effect = Exception
    response = group_logged_in_client.get(url)
    assert response.context["products_exist"] is None


@pytest.mark.django_db
def test_does_not_check_proudcts_exist_when_product_range_is_eol(
    mock_stock_manager, product_range, group_logged_in_client, url
):
    product_range.is_end_of_line = True
    product_range.save()
    response = group_logged_in_client.get(url)
    assert response.context["products_exist"] is None
    mock_stock_manager.products_exist.assert_not_called()
