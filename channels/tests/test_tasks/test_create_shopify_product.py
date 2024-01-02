from unittest import mock

import pytest

from channels.tasks import create_shopify_product


@pytest.fixture
def mock_shopify_listing():
    with mock.patch("channels.tasks.models.shopify_models.ShopifyListing") as m:
        yield m


@pytest.fixture
def mock_shopify_update():
    with mock.patch("channels.tasks.models.shopify_models.ShopifyUpdate") as m:
        yield m


@pytest.fixture
def mock_shopify_listing_manager():
    with mock.patch("channels.tasks.models.shopify_models.ShopifyListingManager") as m:
        yield m


@pytest.fixture
def listing_pk():
    return 489


@pytest.fixture
def update_pk():
    return 304


def test_create_shopify_product_gets_listing(
    mock_shopify_listing,
    mock_shopify_update,
    mock_shopify_listing_manager,
    listing_pk,
    update_pk,
):
    create_shopify_product(listing_pk=listing_pk, update_pk=update_pk)
    mock_shopify_listing.objects.get.assert_called_once_with(pk=listing_pk)


def test_create_shopify_product_gets_update(
    mock_shopify_listing,
    mock_shopify_update,
    mock_shopify_listing_manager,
    listing_pk,
    update_pk,
):
    create_shopify_product(listing_pk=listing_pk, update_pk=update_pk)
    mock_shopify_update.objects.get.assert_called_once_with(pk=update_pk)


def test_create_shopify_product_calls_create_listing(
    mock_shopify_listing,
    mock_shopify_update,
    mock_shopify_listing_manager,
    listing_pk,
    update_pk,
):
    create_shopify_product(listing_pk=listing_pk, update_pk=update_pk)
    mock_shopify_listing_manager.create_listing.assert_called_once_with(
        mock_shopify_listing.objects.get.return_value
    )


def test_create_shopify_product_sets_update_complete(
    mock_shopify_listing,
    mock_shopify_update,
    mock_shopify_listing_manager,
    listing_pk,
    update_pk,
):
    create_shopify_product(listing_pk=listing_pk, update_pk=update_pk)
    mock_shopify_update.objects.get.return_value.set_complete.assert_called_once_with()


def test_create_shopify_product_handles_update_error(
    mock_shopify_listing,
    mock_shopify_update,
    mock_shopify_listing_manager,
    listing_pk,
    update_pk,
):
    mock_shopify_listing_manager.create_listing.side_effect = Exception()
    with pytest.raises(Exception):
        create_shopify_product(listing_pk=listing_pk, update_pk=update_pk)
    mock_shopify_update.objects.get.return_value.set_error.assert_called_once_with()
