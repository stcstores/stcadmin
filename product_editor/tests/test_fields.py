"""Tests for Product Editor form fields."""

import json
from decimal import Decimal

from django import forms
from django.core.exceptions import ValidationError

from inventory import models
from inventory.tests import fixtures
from product_editor.editor_manager import ProductEditorBase
from product_editor.forms import fields
from stcadmin.tests.stcadmin_test import STCAdminTest


class FieldTest(STCAdminTest):
    """Base class for testing custom fields."""

    def get_form_class(self, field=None):
        """Return the test form class."""
        fields = self.get_fields(field=field)

        class TempForm(forms.Form):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.fields = fields

        return TempForm

    def get_field(self):
        """Return the field to be tested."""
        raise NotImplementedError

    def get_fields(self, field=None):
        """Return the fields for the form."""
        if field is None:
            field = self.get_field()
        return {"field": field}

    def make_form_data(self, input):
        """Return the data input for the form."""
        return {"field": input}

    def valid_check(self, input, expected=None, field=None):
        """Test a valid input value."""
        form = self.get_form(input, field=field)
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
        self.assertFalse(
            form.is_valid(),
            msg=(
                f"Form is valid."
                f"Form.data: {form.data} form.cleaned_data: {form.cleaned_data}."
            ),
        )
        self.assertNotEqual(len(form.errors), 0)

    def get_form(self, input, field=None):
        """Return the form to be tested."""
        form_class = self.get_form_class(field=field)
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

    def test_empty(self):
        self.invalid_check(input="")

    def test_title_disallowed_characters(self):
        self.valid_check(input="Hello world", expected="Hello world")
        self.invalid_check(input="Hello ~ world %")


class TestTitleFieldNotRequired(FieldTest):
    def get_field(self):
        return fields.Title(required=False)

    def test_empty(self):
        self.valid_check(input="", expected="")

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


class TestVATRateField(FieldTest):
    def setUp(self):
        super().setUp()
        self.VAT_rate = models.VATRate.objects.create(
            VAT_rate_ID="8", name="Standard VAT", percentage="0.2"
        )

    def get_field(self):
        return fields.VATRate()

    def test_field(self):
        self.valid_check(input=self.VAT_rate.id, expected=self.VAT_rate)
        self.invalid_check(input=67)

    def test_empty(self):
        self.invalid_check(input="")


class TestNotRequiredVATRateField(TestVATRateField):
    def get_field(self):
        return fields.VATRate(required=False)

    def test_empty(self):
        self.valid_check(input="", expected=None)


class TestSupplierField(FieldTest):
    def setUp(self):
        super().setUp()
        self.supplier = models.Supplier.objects.create(
            name="Things Inc", product_option_value_ID="38493", factory_ID="298489"
        )

    def get_field(self):
        return fields.Supplier()

    def test_field(self):
        self.valid_check(input=self.supplier.id, expected=self.supplier)
        self.invalid_check(input=67)

    def test_empty(self):
        self.invalid_check(input="")


class TestNotRequiredSupplierField(TestSupplierField):
    def get_field(self):
        return fields.Supplier(required=False)

    def test_empty(self):
        self.valid_check(input="", expected=None)


class TestPackageTypeField(FieldTest):
    def setUp(self):
        super().setUp()
        self.package_type = models.PackageType.objects.create(
            name="Standard Delivery",
            product_option_value_ID="38493",
            large_letter_compatible=False,
        )

    def get_field(self):
        return fields.PackageType()

    def test_field(self):
        self.valid_check(input=self.package_type.id, expected=self.package_type)
        self.invalid_check(input=67)

    def test_empty(self):
        self.invalid_check(input="")


class TestNotRequiredPackageTypeField(TestPackageTypeField):
    def get_field(self):
        return fields.PackageType(required=False)

    def test_empty(self):
        self.valid_check(input="", expected=None)


class TestInternationalShippingField(FieldTest):
    def setUp(self):
        super().setUp()
        self.international_shipping = models.InternationalShipping.objects.create(
            name="Standard Delivery", product_option_value_ID="38493"
        )

    def get_field(self):
        return fields.InternationalShipping()

    def test_field(self):
        self.valid_check(
            input=self.international_shipping.id, expected=self.international_shipping
        )
        self.invalid_check(input=67)

    def test_empty(self):
        self.invalid_check(input="")


class TestNotRequiredInternationalShippingField(TestInternationalShippingField):
    def get_field(self):
        return fields.InternationalShipping(required=False)

    def test_empty(self):
        self.valid_check(input="", expected=None)


class TestDepartmentField(FieldTest):
    def setUp(self):
        super().setUp()
        self.department = models.Department.objects.create(
            name="Department", product_option_value_ID="389382"
        )

    def get_field(self):
        return fields.Department()

    def test_field(self):
        self.valid_check(input=self.department.id, expected=self.department)
        self.invalid_check(input=67)

    def test_empty(self):
        self.invalid_check(input="")


class TestNotRequiredDepartmentField(TestDepartmentField):
    def get_field(self):
        return fields.Department(required=False)

    def test_empty(self):
        self.valid_check(input="", expected=None)


class TestPartialProductOptionValueSelectField(
    fixtures.EditingProductFixture, FieldTest
):
    def get_field(self):
        return fields.PartialProductOptionValueSelect(
            edit=self.product_edit, product_option=self.colour_product_option
        )

    def test_field(self):
        product_option = self.red_product_option_value
        self.valid_check(input=product_option.id, expected=product_option)
        self.invalid_check(input=67)

    def test_empty(self):
        self.valid_check(input="", expected=None)

    def test_label_from_instance_method(self):
        product_option = self.product_edit.product_option_values.all()[0]
        self.assertEqual(
            self.get_field().label_from_instance(product_option), product_option.value
        )


class TestBrandField(FieldTest):
    def setUp(self):
        super().setUp()
        self.brand = models.Brand.objects.create(
            name="Shiny Things", product_option_value_ID="389382"
        )

    def get_field(self):
        return fields.Brand()

    def test_field(self):
        self.valid_check(input=self.brand.id, expected=self.brand)
        self.invalid_check(input=67)

    def test_empty(self):
        self.invalid_check(input="")


class TestNotRequiredBrandField(TestBrandField):
    def get_field(self):
        return fields.Brand(required=False)

    def test_empty(self):
        self.valid_check(input="", expected=None)


class TestManufacturerField(FieldTest):
    def setUp(self):
        super().setUp()
        self.manufacturer = models.Manufacturer.objects.create(
            name="Shiny Things", product_option_value_ID="389382"
        )

    def get_field(self):
        return fields.Manufacturer()

    def test_field(self):
        self.valid_check(input=self.manufacturer.id, expected=self.manufacturer)
        self.invalid_check(input=67)

    def test_empty(self):
        self.invalid_check(input="")


class TestNotRequiredManufacturerField(TestManufacturerField):
    def get_field(self):
        return fields.Manufacturer(required=False)

    def test_empty(self):
        self.valid_check(input="", expected=None)


class TestGenderField(FieldTest):
    def setUp(self):
        super().setUp()
        self.gender = models.Gender.objects.create(
            name="mens", readable_name="Mens", product_option_value_ID="389382"
        )

    def get_field(self):
        return fields.Gender()

    def test_field(self):
        self.valid_check(input=self.gender.id, expected=self.gender)
        self.invalid_check(input=67)

    def test_empty(self):
        self.valid_check(input="", expected=None)


class TestSelectProductOptionField(FieldTest):
    def setUp(self):
        super().setUp()
        self.product_option = models.ProductOption.objects.create(
            name="Design", product_option_ID="384593"
        )

    def get_field(self):
        return fields.SelectProductOption()

    def test_field(self):
        self.valid_check(input=self.product_option.id, expected=self.product_option)
        self.invalid_check(input=67)

    def test_empty(self):
        self.invalid_check(input="")


class TestSelectProductOptionFieldWithProduct(
    TestSelectProductOptionField, fixtures.VariationProductRangeFixture
):
    fixtures = fixtures.VariationProductRangeFixture.fixtures

    def setUp(self):
        super().setUp()
        self.new_product_option = models.ProductOption.objects.create(
            name="Shoe Size", product_option_ID="384938"
        )

    def get_field(self):
        return fields.SelectProductOption(product_range=self.product_range)

    def test_field(self):
        self.valid_check(
            input=self.new_product_option.id, expected=self.new_product_option
        )
        self.invalid_check(input="670")
        self.invalid_check(input=self.colour_product_option.id)


class TestNotRequiredSelectProductOptionField(TestSelectProductOptionField):
    def get_field(self):
        return fields.SelectProductOption(required=False)

    def test_empty(self):
        self.valid_check(input="", expected=None)


class TestNotRequiredSelectProductOptionFieldWithProduct(
    TestSelectProductOptionFieldWithProduct
):
    def get_field(self):
        return fields.SelectProductOption(
            required=False, product_range=self.product_range
        )

    def test_empty(self):
        self.valid_check(input="", expected=None)


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


class BaseWarehouseAndBayFieldTest(fixtures.ProductRequirementsFixture):

    WAREHOUSE_KEY = ProductEditorBase.WAREHOUSE
    BAY_KEY = ProductEditorBase.BAYS


class TestWarehouse(BaseWarehouseAndBayFieldTest, FieldTest):
    fixtures = fixtures.ProductRequirementsFixture.fixtures

    def get_field(self):
        return fields.Warehouse()

    def test_field(self):
        self.valid_check(input=self.warehouse_1.id, expected=self.warehouse_1)
        self.invalid_check(input=67)

    def test_empty(self):
        self.invalid_check(input="")


class BaseLocationFieldTest(BaseWarehouseAndBayFieldTest):
    def test_single_primary_bay(self):
        self.valid_check(
            input=[self.warehouse_1_bay_1.id], expected=[self.warehouse_1_bay_1.id]
        )

    def test_multiple_primary_bays(self):
        self.valid_check(
            input=[self.warehouse_1_bay_1.id, self.warehouse_1_bay_2.id],
            expected=[self.warehouse_1_bay_1.id, self.warehouse_1_bay_2.id],
        )

    def test_default_bay_is_removed_when_other_primary_bays_are_passed(self):
        self.valid_check(
            input=[self.warehouse_1_defualt_bay.id, self.warehouse_1_bay_2.id],
            expected=[self.warehouse_1_bay_2.id],
        )

    def test_default_bay_is_not_removed_when_no_other_primary_bays_are_passed(self):
        self.valid_check(
            input=[self.warehouse_1_defualt_bay.id],
            expected=[self.warehouse_1_defualt_bay.id],
        )


class TestLocationFieldWithLocation(BaseLocationFieldTest, FieldTest):
    def get_field(self):
        return fields.Location(department=self.warehouse_1)

    def test_default_bay_is_added_for_empty_input(self):
        self.valid_check(input=[], expected=[self.warehouse_1_defualt_bay.id])


class TestLocationFieldWithoutLocation(BaseLocationFieldTest, FieldTest):
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
                self.WAREHOUSE_KEY: self.warehouse_1.id,
                self.BAY_KEY: [self.warehouse_1_bay_1.id],
            },
            expected={
                self.WAREHOUSE_KEY: self.warehouse_1,
                self.BAY_KEY: [self.warehouse_1_bay_1],
            },
        )


class TestDimensionsField(FieldTest):
    def get_field(self):
        return fields.Dimensions()

    def make_form_data(self, input):
        return {f"field_{i}": value for i, value in enumerate(input.values())}

    def test_field(self):
        self.valid_check(
            input={"height": 50, "length": 154, "width": 97},
            expected={"height": 50, "length": 154, "width": 97},
        )
        self.valid_check(
            input={"height": 50, "length": 154},
            expected={"height": 50, "length": 154, "width": 0},
        )
        self.valid_check({"height": 50, "length": 154, "width": 0})
        self.valid_check(input={}, expected={"height": 0, "length": 0, "width": 0})


class ListFieldTests:
    def test_field(self):
        self.valid_check(
            input=json.dumps(["One", "Two Three Four", "Five", "Six", "Seven"]),
            expected=["One", "Two Three Four", "Five", "Six", "Seven"],
        )

    def test_one_input(self):
        self.valid_check(input=json.dumps(["One"]), expected=["One"])

    def test_two_inputs(self):
        self.valid_check(
            input=json.dumps(["One", "Two Three Four"]),
            expected=["One", "Two Three Four"],
        )

    def test_three_inputs(self):
        self.valid_check(
            input=json.dumps(["One", "Two Three Four", "Five"]),
            expected=["One", "Two Three Four", "Five"],
        )

    def test_four_inputs(self):
        self.valid_check(
            input=json.dumps(["One", "Two Three Four", "Five", "Six"]),
            expected=["One", "Two Three Four", "Five", "Six"],
        )

    def test_six_inputs(self):
        self.invalid_check(
            input=json.dumps(["One", "Two Three Four", "Five", "Six", "Seven", "Eight"])
        )

    def test_empty_input(self):
        self.valid_check(input=json.dumps([]), expected=[])


class TestAmazonBulletPointsField(ListFieldTests, FieldTest):
    def get_field(self):
        return fields.AmazonBulletPoints()


class TestAmazonSearchTermsField(ListFieldTests, FieldTest):
    def get_field(self):
        return fields.AmazonSearchTerms()
