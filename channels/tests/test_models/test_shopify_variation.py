from decimal import Decimal

import pytest

from channels.models.shopify_models import ShopifyListing
from inventory.models import BaseProduct


@pytest.fixture
def shopify_variation(shopify_variation_factory):
    return shopify_variation_factory.create()


@pytest.mark.django_db
def test_full_clean(shopify_variation):
    assert shopify_variation.full_clean() is None


@pytest.mark.django_db
def test_has_listing_attribute(shopify_variation):
    assert isinstance(shopify_variation.listing, ShopifyListing)


@pytest.mark.django_db
def test_has_product_attribute(shopify_variation):
    assert isinstance(shopify_variation.product, BaseProduct)


@pytest.mark.django_db
def test_has_price_attribute(shopify_variation):
    assert isinstance(shopify_variation.price, Decimal)


@pytest.mark.django_db
def test_has_variant_id_attribute(shopify_variation):
    assert isinstance(shopify_variation.variant_id, int)


@pytest.mark.django_db
def test_has_inventory_item_id_attribute(shopify_variation):
    assert isinstance(shopify_variation.inventory_item_id, int)


# Test Methods


@pytest.mark.django_db
def test_str_method(shopify_variation):
    assert str(shopify_variation) == shopify_variation.product.sku
