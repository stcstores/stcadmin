from unittest.mock import patch

from inventory import forms, models
from inventory.forms.locations import LocationsForm
from inventory.tests.test_models.test_products import SetupVariationProductRange

from .form_test import FormTest


class SetupLocationsForm:
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.warehouse = models.Warehouse.objects.create(
            name="Warehouse", warehouse_ID="2894032", abriviation="WH"
        )
        cls.bays = [
            models.Bay.objects.create(
                name="Bay 1", bay_ID="384932", warehouse=cls.warehouse
            ),
            models.Bay.objects.create(
                name="Bay 2", bay_ID="435435", warehouse=cls.warehouse
            ),
            models.Bay.objects.create(
                name="Bay 3", bay_ID="834345", warehouse=cls.warehouse
            ),
            models.Bay.objects.create(
                name="Bay 4", bay_ID="643438", warehouse=cls.warehouse
            ),
        ]
        for product in cls.variations:
            product.bays.set(cls.bays)
        cls.form_data = {
            LocationsForm.LOCATION + "_0": cls.warehouse.id,
            LocationsForm.LOCATION + "_1": [bay.id for bay in cls.bays],
        }


class TestLocationsForm(SetupLocationsForm, SetupVariationProductRange, FormTest):
    def test_locations_form(self):
        form = LocationsForm(self.form_data, product=self.product, user=self.user)
        self.assert_form_is_valid(form)
        self.assertEqual(
            form.cleaned_data[LocationsForm.LOCATION][LocationsForm.WAREHOUSE],
            self.warehouse,
        )
        self.assertEqual(
            form.cleaned_data[LocationsForm.LOCATION][LocationsForm.BAYS], self.bays
        )
        self.assertEqual(form.cleaned_data[LocationsForm.BAYS], self.bays)

    def test_initial(self):
        form = LocationsForm(self.form_data, product=self.product, user=self.user)
        initial = form.get_initial()
        self.assertEqual(
            initial,
            {
                LocationsForm.LOCATION: {
                    LocationsForm.WAREHOUSE: self.warehouse.id,
                    LocationsForm.BAYS: [bay.id for bay in self.bays],
                }
            },
        )

    def test_initial_with_no_bays(self):
        self.product.bays.set([])
        form = LocationsForm(self.form_data, product=self.product, user=self.user)
        initial = form.get_initial()
        self.assertEqual(initial, {})

    def test_mixed_warehouses(self):
        second_warehouse = models.Warehouse.objects.create(
            name="Warehouse 2", abriviation="WH2", warehouse_ID="3849382"
        )
        second_warehouse_bay = models.Bay.objects.create(
            name="Second Warehouse Bay", warehouse=second_warehouse, bay_ID="954832"
        )
        self.product.bays.set([self.bays[0].id, second_warehouse_bay.id])
        with self.assertRaises(ValueError):
            LocationsForm(product=self.product, user=self.user)

    @patch("inventory.forms.locations.ProductUpdater")
    def test_save_method(self, mock_updater):
        mock_updater.return_value = mock_updater
        form = LocationsForm(self.form_data, product=self.product, user=self.user)
        self.assert_form_is_valid(form)
        form.save()
        mock_updater.assert_called_once_with(self.product, self.user)
        mock_updater.set_bays.assert_called_once_with(self.bays)


class TestLocationsFormSet(SetupLocationsForm, SetupVariationProductRange, FormTest):
    def test_locations_formset(self):
        forms.LocationsFormSet(
            form_kwargs=[{"product": _} for _ in self.product_range.products()]
        )

    def test_initial(self):
        formset = forms.LocationsFormSet(
            form_kwargs=[
                {"product": _, "user": self.user} for _ in self.product_range.products()
            ]
        )
        initial = formset[0].get_initial()
        self.assertEqual(
            initial,
            {
                LocationsForm.LOCATION: {
                    LocationsForm.WAREHOUSE: self.warehouse.id,
                    LocationsForm.BAYS: [bay.id for bay in self.bays],
                }
            },
        )
