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
    return reverse("inventory:channel_links", kwargs={"range_pk": product_range.pk})


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.fixture(autouse=True)
def mock_stock_manager():
    with mock.patch("inventory.views.productrange.StockManager") as mock_stock_manager:
        yield mock_stock_manager


@pytest.mark.django_db
def test_uses_template(get_response):
    assert "inventory/product_range/channel_links.html" in (
        t.name for t in get_response.templates
    )


@pytest.mark.django_db
def test_product_range_in_context(product_range, get_response):
    assert get_response.context["product_range"] == product_range


@pytest.mark.django_db
def test_products_in_context(products, get_response):
    assert set(get_response.context["products"]) == set(products)


@pytest.mark.django_db
def test_gets_product_links(mock_stock_manager, products, get_response):
    mock_stock_manager.channel_links.assert_called_once_with(
        *[product.sku for product in products]
    )


@pytest.mark.django_db
def test_adds_channel_links_to_products(mock_stock_manager, products, get_response):
    mock_channel_links = mock_stock_manager.channel_links.return_value.get.return_value
    mock_stock_manager.channel_links.return_value.get.assert_has_calls(
        (mock.call(product.sku, []) for product in products)
    )
    for product in get_response.context["products"]:
        assert hasattr(product, "channel_links")
        assert product.channel_links == mock_channel_links
