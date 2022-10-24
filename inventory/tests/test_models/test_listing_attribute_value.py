import datetime as dt

import pytest

from inventory import models


@pytest.fixture
def listing_attribute_value(listing_attribute_value_factory):
    listing_attribute_value = listing_attribute_value_factory.create()
    listing_attribute_value.full_clean()
    return listing_attribute_value


@pytest.mark.django_db
def test_listing_attribute_value_product_attribute(listing_attribute_value):
    assert isinstance(listing_attribute_value.product, models.BaseProduct)


@pytest.mark.django_db
def test_listing_attribute_value_listing_attribute_attribute(listing_attribute_value):
    assert isinstance(
        listing_attribute_value.listing_attribute, models.ListingAttribute
    )


@pytest.mark.django_db
def test_listing_attribute_value_has_value_attribute(listing_attribute_value):
    assert isinstance(listing_attribute_value.value, str)
    assert len(listing_attribute_value.value) > 0


@pytest.mark.django_db
def test_listing_attribute_value_has_created_at_attribute(listing_attribute_value):
    assert isinstance(listing_attribute_value.created_at, dt.datetime)


@pytest.mark.django_db
def test_listing_attribute_value_has_modified_at_attribute(listing_attribute_value):
    assert isinstance(listing_attribute_value.modified_at, dt.datetime)


@pytest.mark.django_db
def test_listing_attribute_value_str_method(listing_attribute_value_factory):
    listing_attribute_value = listing_attribute_value_factory.create(
        product__sku="AAA-AAA-AAA", listing_attribute__name="New Listing Attribute"
    )
    assert (
        str(listing_attribute_value)
        == "ListingAttributeValue: AAA-AAA-AAA - New Listing Attribute"
    )
