"""Tests for Product Editor form fields."""

from decimal import Decimal

from django import forms
from django.core.exceptions import ValidationError
from django.test import TestCase

from inventory import models
from product_editor.forms import fields


class TestField(TestCase):
    """Tests for Product Editor form fields."""

    def setUp(self):
        """Create product option."""
        self.test_option = models.ProductOption(
            name="TestOption", product_option_ID=9823
        )
        self.test_option.save()

    def check_field(self, field, input, valid, expected=None):
        """Check form validation."""
        pass

        class TempForm(forms.Form):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.fields["field"] = field

        form = TempForm({"field": input})
        form.is_valid()
        if valid is True and expected is not None:
            self.assertEqual(form.cleaned_data["field"], expected)
        elif valid is False:
            self.assertNotEqual(len(form.errors), 0)

    def test_title_disallowed_characters(self):
        """Test Title field class allowed characters."""
        field = fields.Title()
        field.validate("Hello World")
        with self.assertRaises(ValidationError):
            field.validate("Hello ~ world %")

    def test_option_field_disallowed_characters(self):
        """Test option field allowed characters."""
        field = fields.VariationOptions(product_option=self.test_option)
        field.allowed_characters = []
        field.validate(["Hello World"])
        field.validate(["Hello World", "Hello Earth"])
        with self.assertRaises(ValidationError):
            field.validate(["Hello + (world) ."])
        with self.assertRaises(ValidationError):
            field.validate(["Hello-world"])
        with self.assertRaises(ValidationError):
            field.validate(["Hello ~ world"])

    def test_option_field_allowed_characters(self):
        """Test option field allowed characters."""
        field = fields.VariationOptions(product_option=self.test_option)
        field.allowed_characters = ["+", "-", ".", "/", "'", '"', "(", ")"]
        field.validate(["Hello World"])
        field.validate(["Hello World", "Hello Earth"])
        field.validate(["Hello + (world) ."])
        field.validate(["Hello-world"])
        with self.assertRaises(ValidationError):
            field.validate(["Hello ~ world"])

    def test_description_disallowed_characters(self):
        """Test Description field class allowed characters."""
        field = fields.Description()
        self.check_field(
            field=field, input="Hello World", valid=True, expected="Hello World"
        )
        self.check_field(
            field=field, input="H + (world) .", valid=True, expected="H + (world) ."
        )
        self.check_field(field=field, input="hello~world", valid=False)
        self.check_field(field=field, input="hello ~ world", valid=False)

    def test_clean_description(self):
        """Test the clean method of the Description field."""
        field = fields.Description()
        self.check_field(
            field=field, input="Hello World!", valid=True, expected="Hello World!"
        )
        self.check_field(
            field=field, input="Hello&nbsp;World!", valid=True, expected="Hello World!"
        )
        self.check_field(
            field=field, input="Hello  World!", valid=True, expected="Hello World!"
        )
        self.check_field(
            field=field, input="Hello   World!", valid=True, expected="Hello World!"
        )
        self.check_field(
            field=field, input="Hello    World!", valid=True, expected="Hello World!"
        )

    def test_barcode_validataion(self):
        """Test the validation of the Barcode field."""
        field = fields.Barcode()
        self.check_field(field=field, input="123456789", valid=True)
        self.check_field(field=field, input="1234a6789", valid=False)
        self.check_field(field=field, input="1234/6789", valid=False)
        self.check_field(field=field, input="1234 6789", valid=False)

    def test_price_field(self):
        """Test the price field validation."""
        field = fields.Price()
        self.check_field(field=field, input="5.6", valid=True, expected=Decimal("5.6"))
        self.check_field(field=field, input="5", valid=True, expected=Decimal("5"))
        self.check_field(
            field=field, input="5.69", valid=True, expected=Decimal("5.69")
        )
        self.check_field(field=field, input="hello", valid=False)
        self.check_field(field=field, input="5.689", valid=False)
