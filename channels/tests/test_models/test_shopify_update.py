import datetime as dt

import pytest

from channels.models.shopify_models import ShopifyListing, ShopifyUpdate


@pytest.fixture
def shopify_update(shopify_update_factory):
    return shopify_update_factory.create()


@pytest.mark.django_db
def test_full_clean(shopify_update):
    assert shopify_update.full_clean() is None


@pytest.mark.django_db
def test_has_listing_attribute(shopify_update):
    assert isinstance(shopify_update.listing, ShopifyListing)


@pytest.mark.django_db
def test_has_operation_type_attribute(shopify_update):
    assert isinstance(shopify_update.operation_type, str)


@pytest.mark.django_db
def test_has_created_at_attribute(shopify_update):
    assert isinstance(shopify_update.created_at, dt.datetime)


@pytest.mark.django_db
def test_has_completed_at_attribute(shopify_update):
    assert isinstance(shopify_update.completed_at, dt.datetime)


@pytest.mark.django_db
def test_has_error_attribute(shopify_update):
    assert isinstance(shopify_update.error, bool)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "operation_type",
    (ShopifyUpdate.CREATE_PRODUCT, ShopifyUpdate.UPDATE_PRODUCT),
)
def test_operation_type_values(operation_type, shopify_update_factory):
    shopify_update = shopify_update_factory.create(operation_type=operation_type)
    assert shopify_update.full_clean() is None


# Test Methods


@pytest.mark.django_db
def test_set_complete_method(shopify_update_factory):
    shopify_update = shopify_update_factory.create(completed_at=None)
    shopify_update.set_complete()
    assert isinstance(shopify_update.completed_at, dt.datetime)
    assert shopify_update.error is False


@pytest.mark.django_db
def test_set_error_method(shopify_update_factory):
    shopify_update = shopify_update_factory.create(completed_at=None)
    shopify_update.set_error()
    assert isinstance(shopify_update.completed_at, dt.datetime)
    assert shopify_update.error is True


# Test Manager Methods


@pytest.fixture
def shopify_listing(shopify_listing_factory):
    return shopify_listing_factory.create()


@pytest.mark.django_db
def test_start_upload_listing_raises_if_update_in_progress(
    shopify_update_factory, shopify_listing
):
    shopify_update_factory.create(listing=shopify_listing, completed_at=None)
    with pytest.raises(Exception):
        ShopifyUpdate.objects.start_upload_listing(shopify_listing)


@pytest.mark.django_db
def test_start_upload_listing_creating_product(shopify_listing_factory):
    listing = shopify_listing_factory.create(product_id=None)
    ShopifyUpdate.objects.start_upload_listing(listing)
    assert ShopifyUpdate.objects.filter(
        listing=listing, operation_type=ShopifyUpdate.CREATE_PRODUCT
    ).exists()


@pytest.mark.django_db
def test_start_upload_listing_updating_product(shopify_listing):
    ShopifyUpdate.objects.start_upload_listing(shopify_listing)
    assert ShopifyUpdate.objects.filter(
        listing=shopify_listing, operation_type=ShopifyUpdate.UPDATE_PRODUCT
    ).exists()
