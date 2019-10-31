"""Tests for Product Editor form validators."""

from django.core.exceptions import ValidationError

from product_editor.forms.fieldtypes import Validators
from stcadmin.tests.stcadmin_test import STCAdminTest


class TestValidators(STCAdminTest):
    """Tests for Product Editor form validators."""

    def test_alphanumeric(self):
        """Test Validators.alphanumeric works correctly."""
        Validators.alphanumeric("a")
        Validators.alphanumeric("1")
        Validators.alphanumeric(" ")
        with self.assertRaises(ValidationError):
            Validators.alphanumeric("!")
        with self.assertRaises(ValidationError):
            Validators.alphanumeric("~")
        with self.assertRaises(ValidationError):
            Validators.alphanumeric("&")
        with self.assertRaises(ValidationError):
            Validators.alphanumeric("0.5")

    def test_numeric(self):
        """Test Validators.numierc works correctly."""
        Validators.numeric("1")
        Validators.numeric("25")
        with self.assertRaises(ValidationError):
            Validators.numeric("!")
        with self.assertRaises(ValidationError):
            Validators.numeric("0.5")
        with self.assertRaises(ValidationError):
            Validators.numeric(" ")
        with self.assertRaises(ValidationError):
            Validators.numeric("a")

    def test_allow_character(self):
        """Test Validators.allow_characters works correctly."""
        Validators.allow_characters("HelloWorld", [])
        Validators.allow_characters("Hello World", [])
        Validators.allow_characters("Hello World 2", [])
        Validators.allow_characters("Hello, World!", [",", "!"])
        with self.assertRaises(ValidationError):
            Validators.allow_characters("Hello, World!", [])
        with self.assertRaises(ValidationError):
            Validators.allow_characters("Hello World 2.5", [])

    def test_disallow_characters(self):
        """Test Validators.disallow_characters works correctly."""
        Validators.disallow_characters("Helloworld", [])
        Validators.disallow_characters("Hello world", [])
        Validators.disallow_characters("Helloworld ~", [])
        Validators.disallow_characters("Helloworld", ["~"])
        Validators.disallow_characters("2", ["~"])
        with self.assertRaises(ValidationError):
            Validators.disallow_characters("Helloworld ~", ["~"])
            Validators.disallow_characters("2.5", ["."])
