"""Tests for Product Editor form fields."""

from decimal import Decimal

from django import forms
from django.core.exceptions import ValidationError
from django.test import TestCase

from inventory import models
from product_editor.editor_manager import ProductEditorBase
from product_editor.forms import fields


class FieldTest(TestCase):
    """Base class for testing custom fields."""

    def get_form_class(self):
        """Return the test form class."""
        fields = self.get_fields()

        class TempForm(forms.Form):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.fields = fields

        return TempForm

    def get_field(self):
        """Return the field to be tested."""
        raise NotImplementedError

    def get_fields(self):
        """Return the fields for the form."""
        return {"field": self.get_field()}

    def make_form_data(self, input):
        """Return the data input for the form."""
        return {"field": input}

    def valid_check(self, input, expected=None):
        """Test a valid input value."""
        form = self.get_form(input)
        self.assertTrue(
            form.is_valid(),
            msg=f"Form not valid. Data: {form.data} Errors: {form.errors}.",
        )
        if expected is not None:
            self.assertEqual(
                form.cleaned_data.get("field"),
                expected,
                msg=(
                    "Cleaned data did not match expected. "
                    f"form.data: {form.data} form.cleaned_data: {form.cleaned_data}."
                ),
            )

    def invalid_check(self, input):
        """Test an invalid input value."""
        form = self.get_form(input)
        self.assertFalse(form.is_valid())
        self.assertNotEqual(len(form.errors), 0)

    def get_form(self, input):
        """Return the form to be tested."""
        form_class = self.get_form_class()
        form_data = self.make_form_data(input)
        return form_class(form_data)


class TestOptonField(FieldTest):
    """Tests for Product Editor form fields."""

    def setUp(self):
        """Create product option."""
        self.test_option = models.ProductOption(
            name="TestOption", product_option_ID="9823"
        )
        self.test_option.save()
        self.option_values = [
            models.ProductOptionValue(
                value="Hello World",
                product_option=self.test_option,
                product_option_value_ID="13548",
            ),
            models.ProductOptionValue(
                value="Hello Earth",
                product_option=self.test_option,
                product_option_value_ID="68745",
            ),
        ]
        models.ProductOptionValue.objects.bulk_create(self.option_values)

    def get_field(self):
        field = fields.VariationOptions(product_option=self.test_option)
        field.allowed_characters = []
        return field

    def test_option_field_with_single_existing_value(self):

        self.valid_check(
            input=[self.option_values[0].value], expected=[self.option_values[0]]
        )

    def test_option_field_with_multiple_existing_values(self):
        self.valid_check(
            input=[self.option_values[0].value, self.option_values[1].value],
            expected=[self.option_values[0], self.option_values[1]],
        )

    def test_option_field_with_single_new_value(self):
        with self.assertRaises(NotImplementedError):
            # Creating product options is not yet implemented
            self.valid_check(input=["Non Existant Value"])

    def test_option_field_with_multiple_new_values(self):
        with self.assertRaises(NotImplementedError):
            # Creating product options is not yet implemented
            self.valid_check(input=["Non Existant Value", "Another New Value"])

    def test_option_field_with_mixed_new_and_existing_values(self):
        with self.assertRaises(NotImplementedError):
            # Creating product options is not yet implemented
            self.valid_check(input=["Non Existant Value", self.option_values[0].value])

    def test_option_field_disallows_special_characters(self):
        field = self.get_field()
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


class TestTitleField(FieldTest):
    def get_field(self):
        return fields.Title()

    def test_title_disallowed_characters(self):
        self.valid_check(input="Hello world", expected="Hello world")
        self.invalid_check(input="Hello ~ world %")


class TestDescriptionField(FieldTest):
    def get_field(self):
        return fields.Description()

    def test_description_field(self):
        self.valid_check(input="Hello World!", expected="Hello World!")

    def test_description_field_removes_non_breaking_spaces(self):
        self.valid_check(input="Hello&nbsp;World!", expected="Hello World!")

    def test_description_field_removes_excess_spaces(self):
        self.valid_check(input="Hello   World!", expected="Hello World!")
        self.valid_check(input="Hello    World!", expected="Hello World!")

    def test_description_disallowed_characters(self):
        self.valid_check(input="Hello World", expected="Hello World")
        self.valid_check(input="H + (world) .", expected="H + (world) .")
        self.invalid_check(input="hello~world")
        self.invalid_check(input="hello ~ world")


class TestBarcodeField(FieldTest):
    def get_field(self):
        return fields.Barcode()

    def test_barcode_field(self):
        self.valid_check(input="123456789", expected="123456789")

    def test_barcode_field_disallows_letters(self):
        self.invalid_check(input="1234a6789")

    def test_barcode_field_idsallows_puctuation(self):
        self.invalid_check(input="1234/6789")

    def test_barcode_field_disallows_spaces(self):
        self.invalid_check(input="1234 6789")


class TestPriceField(FieldTest):
    def get_field(self):
        return fields.Price()

    def test_price_field_with_one_decimal_place(self):
        self.valid_check(input="5.6", expected=Decimal("5.6"))

    def test_price_field_with_no_decimal(self):
        self.valid_check(input="5", expected=Decimal("5"))

    def test_price_field_with_two_decimal_places(self):
        self.valid_check(input="5.69", expected=Decimal("5.69"))

    def test_price_field_disallows_letters(self):
        self.invalid_check(input="hello")

    def test_price_field_disallows_three_decimal_places(self):
        self.invalid_check(input="5.689")


class BaseWarehouseAndBayFieldTest:
    """Setup locations for testing bay and warehouse fields."""

    WAREHOUSE_KEY = ProductEditorBase.WAREHOUSE
    BAY_KEY = ProductEditorBase.BAYS

    def setUp(self):
        """Create locations for tests."""
        self.warehouse = models.Warehouse(
            name="Warehouse 1", warehouse_ID="52", abriviation="WH"
        )
        self.warehouse.save()
        self.default_bay = models.Bay(
            name="Default Bay", warehouse=self.warehouse, bay_ID="31", is_default=True
        )
        self.default_bay.save()
        self.bays = [
            models.Bay(name=f"Bay_{i}", warehouse=self.warehouse, bay_ID=str(32 + i))
            for i in range(1, 11)
        ]
        models.Bay.objects.bulk_create(self.bays)


class TestWarehouse(BaseWarehouseAndBayFieldTest, FieldTest):
    def get_field(self):
        return fields.Warehouse()

    def test_warehouse_field(self):
        self.valid_check(
            input=self.warehouse.warehouse_ID, expected=self.warehouse.warehouse_ID
        )


class BaseLocationFieldTest(BaseWarehouseAndBayFieldTest):
    """Tests for LocationField both with and without the warehouse kwarg."""

    def test_single_primary_bay(self):
        self.valid_check(input=[self.bays[0].bay_ID], expected=[self.bays[0].bay_ID])

    def test_multiple_primary_bays(self):
        self.valid_check(
            input=[self.bays[0].bay_ID, self.bays[1].bay_ID],
            expected=[self.bays[0].bay_ID, self.bays[1].bay_ID],
        )

    def test_default_bay_is_removed_when_other_primary_bays_are_passed(self):
        self.valid_check(
            input=[self.default_bay.bay_ID, self.bays[1].bay_ID],
            expected=[self.bays[1].bay_ID],
        )

    def test_default_bay_is_not_removed_when_no_other_primary_bays_are_passed(self):
        self.valid_check(
            input=[self.default_bay.bay_ID], expected=[self.default_bay.bay_ID]
        )


class TestLocationFieldWithLocation(BaseLocationFieldTest, FieldTest):
    """Tests for LocationField with the warehouse parameter."""

    def get_field(self):
        return fields.Location(department=self.warehouse)

    def test_default_bay_is_added_for_empty_input(self):
        self.valid_check(input=[], expected=[self.default_bay.bay_ID])


class TestLocationFieldWithoutLocation(BaseLocationFieldTest, FieldTest):
    """Tests for LocationField without the warehouse parameter."""

    def get_field(self):
        return fields.Location()

    def test_empty_input_is_invalid(self):
        self.invalid_check(input=[])


class TestWarhouseBayField(BaseWarehouseAndBayFieldTest, FieldTest):
    def get_field(self):
        return fields.WarehouseBayField()

    def make_form_data(self, input):
        return {f"field_{i}": value for i, value in enumerate(input.values())}

    def test_warehouse_bay_field(self):
        self.valid_check(
            input={
                self.WAREHOUSE_KEY: self.warehouse.warehouse_ID,
                self.BAY_KEY: [self.bays[0].bay_ID],
            },
            expected={
                self.WAREHOUSE_KEY: self.warehouse.warehouse_ID,
                self.BAY_KEY: [self.bays[0].bay_ID],
            },
        )
