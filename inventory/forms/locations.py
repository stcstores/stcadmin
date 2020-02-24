"""Forms for updating product locations."""

from django import forms
from django.core.exceptions import ValidationError

from inventory import models
from product_editor.editor_manager import ProductEditorBase
from product_editor.forms.fields import Department, WarehouseBayField
from stcadmin.forms import KwargFormSet


class DepartmentForm(forms.Form):
    """Form for changing the department of a Product Range."""

    DEPARTMENT = ProductEditorBase.DEPARTMENT

    def __init__(self, *args, **kwargs):
        """Create fields for form."""
        self.product_range = kwargs.pop("product_range")
        super().__init__(*args, **kwargs)
        self.fields[self.DEPARTMENT] = Department()
        self.initial.update(self.get_initial())

    def get_initial(self):
        """Return initial values for form."""
        initial = {}
        department = self.product_range.department
        try:
            department_id = models.Warehouse.used_warehouses.get(
                name=department
            ).warehouse_ID
        except models.Warehouse.DoesNotExist:
            department_id = None
        initial[self.DEPARTMENT] = department_id
        return initial

    def save(self):
        """Update Product Range department."""
        department = models.Warehouse.objects.get(
            warehouse_ID=self.cleaned_data[self.DEPARTMENT]
        )
        self.product_range.department = department.name


class LocationsForm(forms.Form):
    """Form for changing the Warehouse Bays associated with a product."""

    PRODUCT_ID = "product_id"
    PRODUCT_NAME = "product_name"
    STOCK_LEVEL = "stock_level"
    LOCATIONS = "locations"
    WAREHOUSE = ProductEditorBase.WAREHOUSE
    BAYS = ProductEditorBase.BAYS

    product_id = forms.CharField(widget=forms.TextInput(attrs={"class": "product_id"}))
    product_name = forms.CharField(
        disabled=True,
        required=False,
        widget=forms.TextInput(attrs={"size": 200, "class": "product_title"}),
    )
    stock_level = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        """Add fields to form."""
        self.product = kwargs.pop("product")
        super().__init__(*args, **kwargs)
        self.fields[self.LOCATIONS] = WarehouseBayField()
        self.cleaned_data = {}
        self.initial.update(self.get_initial())

    def get_initial(self):
        """Return initial data."""
        initial = {}
        initial[self.PRODUCT_ID] = self.product.id
        initial[self.PRODUCT_NAME] = self.product.full_name
        initial[self.STOCK_LEVEL] = self.product.stock_level
        bays = [bay for bay in models.Bay.objects.filter(bay_ID__in=self.product.bays)]
        warehouses = list(set([bay.warehouse for bay in bays]))
        if warehouses:
            initial[self.LOCATIONS] = {
                self.WAREHOUSE: warehouses[0].warehouse_ID,
                self.BAYS: [bay.bay_ID for bay in bays],
            }
        return initial

    def clean(self):
        """Add list of bay IDs to cleaned data."""
        cleaned_data = super().clean()
        cleaned_data.pop(self.PRODUCT_NAME)
        cleaned_data.pop(self.STOCK_LEVEL)
        if self.LOCATIONS not in cleaned_data:
            raise ValidationError("Invalid Location")
        bays = cleaned_data[self.LOCATIONS][self.BAYS]
        cleaned_data[self.LOCATIONS][self.BAYS] = bays
        return cleaned_data

    def save(self):
        """Update product with new bays."""
        self.product.bays = self.cleaned_data[self.LOCATIONS][self.BAYS]


class LocationsFormSet(KwargFormSet):
    """Formset for updating the locations of all Products within a Range."""

    form = LocationsForm
