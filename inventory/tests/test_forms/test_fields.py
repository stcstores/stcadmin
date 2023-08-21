from unittest import mock

import pytest

from inventory.forms import fields


@pytest.fixture
def variation_option(variation_option_factory):
    return variation_option_factory.create()


@pytest.fixture
def product_option_value_field(variation_option):
    return fields.ProductOptionValueField(variation_option=variation_option)


@pytest.mark.django_db
def test_product_optino_value_field_sets_variation_options(
    product_option_value_field, variation_option
):
    assert product_option_value_field.variation_option == variation_option


@pytest.mark.django_db
def test_product_option_value_field_valid_value(product_option_value_field):
    assert product_option_value_field.valid_value(None) is True


@pytest.mark.django_db
def test_product_option_value_field_sets_allowed_characters(variation_option_factory):
    variation_option = variation_option_factory.create(name="Size")
    field = fields.ProductOptionValueField(variation_option=variation_option)
    assert field.allowed_characters == field.option_allowed_characters["Size"]


@pytest.mark.django_db
def test_product_option_value_field_sets_allowed_characters_to_none(
    variation_option_factory,
):
    variation_option = variation_option_factory.create(name="New Option")
    field = fields.ProductOptionValueField(variation_option=variation_option)
    assert field.allowed_characters is None


@pytest.mark.django_db
@mock.patch("inventory.forms.fields.Validators.allow_characters")
def test_validate_passes_values_to_allow_characters(
    mock_allow_characters, variation_option_factory
):
    values = ["a", "b", "c"]
    variation_option = variation_option_factory.create(name="Size")
    field = fields.ProductOptionValueField(variation_option=variation_option)
    field.validate(values)
    mock_allow_characters.assert_has_calls(
        (mock.call(value, field.allowed_characters) for value in values)
    )


@pytest.mark.django_db
@mock.patch("inventory.forms.fields.Validators.allow_characters")
def test_validate_does_not_validate_when_allowed_characters_is_none(
    mock_allow_characters, variation_option_factory
):
    values = ["a", "b", "c"]
    variation_option = variation_option_factory.create(name="New Option")
    field = fields.ProductOptionValueField(variation_option=variation_option)
    field.validate(values)
    mock_allow_characters.assert_not_called()
