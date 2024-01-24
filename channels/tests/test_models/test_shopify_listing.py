import datetime as dt
from unittest import mock

import pytest
from django.urls import reverse
from django.utils.timezone import make_aware

from inventory.models import ProductRange


@pytest.fixture
def shopify_listing(shopify_listing_factory):
    return shopify_listing_factory.create()


@pytest.mark.django_db
def test_full_clean(shopify_listing):
    assert shopify_listing.full_clean() is None


@pytest.mark.django_db
def test_has_product_range_attribute(shopify_listing):
    assert isinstance(shopify_listing.product_range, ProductRange)


@pytest.mark.django_db
def test_has_title_attribute(shopify_listing):
    assert isinstance(shopify_listing.title, str)


@pytest.mark.django_db
def test_has_description_attribute(shopify_listing):
    assert isinstance(shopify_listing.description, str)


@pytest.mark.django_db
def test_can_add_tags(shopify_listing, shopify_tag_factory):
    tag = shopify_tag_factory.create()
    shopify_listing.tags.add(tag)
    assert shopify_listing.tags.contains(tag)


@pytest.mark.django_db
def test_can_add_collections(shopify_listing, shopify_collection_factory):
    collection = shopify_collection_factory.create()
    shopify_listing.collections.add(collection)
    assert shopify_listing.collections.contains(collection)


@pytest.mark.django_db
def test_has_product_id_attribute(shopify_listing):
    assert isinstance(shopify_listing.product_id, int)


# Test Methods


@pytest.fixture
def mock_shopify_manager():
    with mock.patch(
        "channels.models.shopify_models.shopify_listing.ShopifyManager"
    ) as m:
        yield m


@pytest.fixture
def mock_tasks():
    with mock.patch("channels.models.shopify_models.shopify_listing.tasks") as m:
        yield m


@pytest.fixture
def mock_shopify_update():
    with mock.patch(
        "channels.models.shopify_models.shopify_listing.ShopifyUpdate"
    ) as m:
        yield m


@pytest.mark.django_db
def test_str_method(shopify_listing):
    assert str(shopify_listing) == shopify_listing.product_range.sku


@pytest.mark.django_db
def test_get_absoulute_url_method(shopify_listing):
    assert shopify_listing.get_absolute_url() == reverse(
        "channels:shopify_listing", kwargs={"listing_pk": shopify_listing.pk}
    )


@pytest.mark.django_db
def test_listing_is_active_method_with_no_product_id(
    mock_shopify_manager, shopify_listing_factory
):
    listing = shopify_listing_factory.create(product_id=None)
    assert listing.listing_is_active() is False
    mock_shopify_manager.product_exists.assert_not_called()


@pytest.mark.django_db
def test_listing_is_active_method_with_product_id(
    mock_shopify_manager, shopify_listing
):
    value = shopify_listing.listing_is_active()
    mock_shopify_manager.product_exists.assert_called_once_with(
        shopify_listing.product_id
    )
    assert value == mock_shopify_manager.product_exists.return_value


@pytest.mark.django_db
def test_get_last_update_method(shopify_listing, shopify_update_factory):
    shopify_update_factory.create(
        created_at=make_aware(dt.datetime(2023, 10, 24)), listing=shopify_listing
    )
    new_update = shopify_update_factory.create(
        created_at=make_aware(dt.datetime(2023, 10, 25)), listing=shopify_listing
    )
    assert shopify_listing.get_last_update() == new_update


@pytest.mark.django_db
def test_upload_method_creates_update(mock_shopify_update, mock_tasks, shopify_listing):
    shopify_listing.upload()
    mock_shopify_update.objects.start_upload_listing.assert_called_once_with(
        shopify_listing
    )


@pytest.mark.django_db
def test_upload_creates_product(
    mock_shopify_update, mock_tasks, shopify_listing_factory
):
    shopify_listing = shopify_listing_factory.create(product_id=None)
    shopify_listing.upload()
    mock_tasks.create_shopify_product.delay.assert_called_once_with(
        listing_pk=shopify_listing.pk,
        update_pk=mock_shopify_update.objects.start_upload_listing.return_value.pk,
    )


@pytest.mark.django_db
def test_upload_updates_product(mock_shopify_update, mock_tasks, shopify_listing):
    shopify_listing.upload()
    mock_tasks.update_shopify_product.delay.assert_called_once_with(
        listing_pk=shopify_listing.pk,
        update_pk=mock_shopify_update.objects.start_upload_listing.return_value.pk,
    )


@pytest.mark.django_db
def test_upload_with_error_creating_product(
    mock_shopify_update, mock_tasks, shopify_listing_factory
):
    shopify_listing = shopify_listing_factory.create(product_id=None)
    mock_tasks.create_shopify_product.delay.side_effect = Exception()
    with pytest.raises(Exception):
        shopify_listing.upload()
    mock_shopify_update.objects.start_upload_listing.return_value.set_error.assert_called_once_with()


@pytest.mark.django_db
def test_upload_with_error_updating_product(
    mock_shopify_update, mock_tasks, shopify_listing
):
    mock_tasks.update_shopify_product.delay.side_effect = Exception()
    with pytest.raises(Exception):
        shopify_listing.upload()
    mock_shopify_update.objects.start_upload_listing.return_value.set_error.assert_called_once_with()
