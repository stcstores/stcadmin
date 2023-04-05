from unittest import mock

import pytest
from django.urls import reverse

from inventory import models


@pytest.fixture
def product_pk():
    return 9999


@pytest.fixture
def mock_incomplete_prouct():
    return mock.Mock(status=models.ProductRange.CREATING)


@pytest.fixture
def mock_complete_product():
    return mock.Mock(status=models.ProductRange.COMPLETE)


@pytest.fixture
def url(product_pk):
    return reverse("inventory:discard_new_range", kwargs={"range_pk": product_pk})


@pytest.fixture
def mock_get_object(mock_incomplete_prouct):
    with mock.patch(
        "inventory.views.product_editor.get_object_or_404"
    ) as mock_get_object:
        mock_get_object.return_value = mock_incomplete_prouct
        yield mock_get_object


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


def test_calls_get_object_or_404(mock_get_object, product_pk, get_response):
    mock_get_object.assert_called_once_with(models.ProductRange, pk=product_pk)


def test_deletes_products(mock_get_object, get_response):
    mock_get_object.return_value.products.all.return_value.delete.assert_called_once_with()


def test_deletes_product_range(mock_get_object, get_response):
    mock_get_object.return_value.delete.assert_called_once_with()


def test_redirects(mock_get_object, get_response):
    assert get_response.status_code == 302
    assert get_response["location"] == reverse("inventory:product_search")


def test_prevents_deleting_complete_product_ranges(
    mock_get_object, mock_complete_product, group_logged_in_client, url
):
    mock_get_object.return_value = mock_complete_product
    with pytest.raises(ValueError):
        group_logged_in_client.get(url)
    mock_get_object.return_value.products.all.return_value.delete.assert_not_called()
    mock_get_object.return_value.delete.assert_not_called()
