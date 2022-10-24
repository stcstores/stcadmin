import datetime as dt

import pytest

from inventory import models


@pytest.fixture
def variation_option(variation_option_factory):
    variation_option = variation_option_factory.create()
    variation_option.full_clean()
    return variation_option


@pytest.fixture
def new_variation_option():
    variation_option = models.VariationOption(name="New Variation Option")
    variation_option.save()
    return variation_option


@pytest.mark.django_db
def test_variation_option_has_name_attribute(variation_option):
    assert isinstance(variation_option.name, str)
    assert len(variation_option.name) > 0


@pytest.mark.django_db
def test_variation_option_ordering_attribute_defaults_to_zero(new_variation_option):
    assert new_variation_option.ordering == 0


@pytest.mark.django_db
def test_variation_option_active_attribute_defaults_to_true(new_variation_option):
    assert new_variation_option.active is True


@pytest.mark.django_db
def test_variation_option_created_at_attribute(variation_option):
    assert isinstance(variation_option.created_at, dt.datetime)


@pytest.mark.django_db
def test_variation_option_modified_at_attribute(variation_option):
    assert isinstance(variation_option.modified_at, dt.datetime)


@pytest.mark.django_db
def test_variation_option_str_method(variation_option):
    assert str(variation_option) == variation_option.name
