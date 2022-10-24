import datetime as dt

import pytest

from inventory import models


@pytest.fixture
def variation_option_value(variation_option_value_factory):
    variation_option_value = variation_option_value_factory.create()
    variation_option_value.full_clean()
    return variation_option_value


@pytest.mark.django_db
def test_variation_option_value_product_attribute(variation_option_value):
    assert isinstance(variation_option_value.product, models.BaseProduct)


@pytest.mark.django_db
def test_variation_option_value_variation_option_attribute(variation_option_value):
    assert isinstance(variation_option_value.variation_option, models.VariationOption)


@pytest.mark.django_db
def test_variation_option_value_has_value_attribute(variation_option_value):
    assert isinstance(variation_option_value.value, str)
    assert len(variation_option_value.value) > 0


@pytest.mark.django_db
def test_variation_option_value_has_created_at_attribute(variation_option_value):
    assert isinstance(variation_option_value.created_at, dt.datetime)


@pytest.mark.django_db
def test_variation_option_value_has_modified_at_attribute(variation_option_value):
    assert isinstance(variation_option_value.modified_at, dt.datetime)


@pytest.mark.django_db
def test_variation_option_value_str_method(variation_option_value_factory):
    variation_option_value = variation_option_value_factory.create(
        product__sku="AAA-AAA-AAA", variation_option__name="New Variation Option"
    )
    assert (
        str(variation_option_value)
        == "VariationOptionValue: AAA-AAA-AAA - New Variation Option"
    )
