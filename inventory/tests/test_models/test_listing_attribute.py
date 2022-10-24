import datetime as dt

import pytest

from inventory import models


@pytest.fixture
def listing_attribute(listing_attribute_factory):
    listing_attribute = listing_attribute_factory.create()
    listing_attribute.full_clean()
    return listing_attribute


@pytest.fixture
def new_listing_attribute():
    listing_attribute = models.ListingAttribute(name="New Listing Attribute")
    listing_attribute.save()
    return listing_attribute


@pytest.mark.django_db
def test_listing_attribute_has_name_attribute(listing_attribute):
    assert isinstance(listing_attribute.name, str)
    assert len(listing_attribute.name) > 0


@pytest.mark.django_db
def test_listing_attribute_ordering_attribute_defaults_to_zero(new_listing_attribute):
    assert new_listing_attribute.ordering == 0


@pytest.mark.django_db
def test_listing_attribute_active_attribute_defaults_to_true(new_listing_attribute):
    assert new_listing_attribute.active is True


@pytest.mark.django_db
def test_listing_attribute_created_at_attribute(listing_attribute):
    assert isinstance(listing_attribute.created_at, dt.datetime)


@pytest.mark.django_db
def test_listing_attribute_modified_at_attribute(listing_attribute):
    assert isinstance(listing_attribute.modified_at, dt.datetime)


@pytest.mark.django_db
def test_listing_attribute_str_method(listing_attribute):
    assert str(listing_attribute) == listing_attribute.name
