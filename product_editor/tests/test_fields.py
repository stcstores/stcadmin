"""Tests for Product Editor form fields."""

from django.core.exceptions import ValidationError
from django.test import TestCase
from product_editor.forms import fields


class TestField(TestCase):
    """Tests for Product Editor form fields."""

    def test_title_disallowed_characters(self):
        """Test Field class allowed characters."""
        field = fields.Title()
        field.validate('Hello World')
        with self.assertRaises(ValidationError):
            field.validate('Hello ~ world %')

    def test_option_field_allowed_characters(self):
        """Test option field allowed characters."""
        field = fields.VariationOptions(label='Size', choices=[])
        field = fields.Title()
        field.validate('Hello World')
        with self.assertRaises(ValidationError):
            field.validate('Hello + (world) .')
