from unittest.mock import Mock, call, patch

import pytest

from inventory.models import Products
from inventory.tests import mocks


@pytest.fixture
def mock_CCAPI():
    with patch("inventory.models.products.CCAPI") as mock_CCAPI:
        yield mock_CCAPI


@pytest.fixture
def results():
    return [
        mocks.MockCCAPIProductRange(end_of_line=True),
        mocks.MockCCAPIProductRange(end_of_line=False),
    ]


@pytest.fixture
def products(results):
    products = []
    for result in results:
        products.extend(result.products)
    return products


def test_get_ranges(mock_CCAPI, results, products):
    mock_CCAPI.search_products.return_value = products
    mock_CCAPI.get_range.side_effect = results
    search_text = "product name"
    result = Products.get_ranges(search_text)
    mock_CCAPI.search_products.assert_called_once_with(search_text)
    mock_CCAPI.get_range.assert_has_calls(
        [call(product.id) for product in products], any_order=True
    )
    assert result == results


def test_filter_end_of_line(results):
    assert Products.filter_end_of_line(results) == [results[1]]


def test_filter_not_end_of_line(results):
    assert Products.filter_not_end_of_line(results) == [results[0]]


def test_advanced_get_ranges(mock_CCAPI, results):
    search_text = "product_name"
    only_in_stock = True
    option_matches_id = "28749392"
    mock_CCAPI.get_ranges.return_value = results
    returned = Products.advanced_get_ranges(
        search_text=search_text,
        only_in_stock=only_in_stock,
        option_matches_id=option_matches_id,
    )
    assert mock_CCAPI.get_ranges.called_once_with(
        search_text=search_text,
        only_in_stock=only_in_stock,
        option_matches_id=option_matches_id,
    )
    assert returned == results


def test_get_product_options_method(mock_CCAPI):
    return_value = Mock()
    mock_CCAPI.get_product_options.return_value = return_value
    result = Products.get_product_options()
    mock_CCAPI.get_product_options.assert_called_once()
    assert result == return_value
