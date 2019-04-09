"""Forms for updating product locations."""

from django import forms

from inventory import models
from product_editor.editor_manager import ProductEditorBase
from product_editor.forms.fields import WarehouseBayField
from product_editor.forms.fieldtypes import SelectizeModelChoiceField
from stcadmin.forms import KwargFormSet


class DepartmentForm(forms.Form):
    """Form for changing the department of a Product Range."""

    DEPARTMENT = ProductEditorBase.DEPARTMENT

    def __init__(self, *args, **kwargs):
        """Create fields for form."""
        self.product_range = kwargs.pop("product_range")
        super().__init__(*args, **kwargs)
        self.fields[self.DEPARTMENT] = SelectizeModelChoiceField(
            queryset=models.Department.objects.filter(inactive=False)
        )
        self.initial.update(self.get_initial())

    def get_initial(self):
        """Return initial values for form."""
        initial = {}
        initial[self.DEPARTMENT] = self.product_range.department
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
    LOCATIONS = "locations"
    WAREHOUSE = ProductEditorBase.WAREHOUSE
    BAYS = ProductEditorBase.BAYS

    product_id = forms.CharField(widget=forms.TextInput(attrs={"class": "product_id"}))
    product_name = forms.CharField(
        disabled=True,
        required=False,
        widget=forms.TextInput(attrs={"size": 200, "class": "product_title"}),
    )

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
        initial[self.PRODUCT_NAME] = self.product.variation() or self.product.name
        bays = self.product.bays.all()
        warehouses = list(set([bay.warehouse for bay in bays]))
        if len(warehouses) > 1:
            self.add_error(self.LOCATIONS, "Mixed warehouses.")
        elif len(warehouses) == 1:
            initial[self.LOCATIONS] = {
                self.WAREHOUSE: warehouses[0].warehouse_ID,
                self.BAYS: [bay.bay_ID for bay in bays],
            }
        return initial

    def get_warehouse_for_bays(self, bay_IDs):
        """Return warehouse for bay_IDs."""
        if len(bay_IDs) == 0:
            return None
        bays = models.Bay.objects.filter(
            bay_ID__in=[int(bay_ID) for bay_ID in bay_IDs]
        ).all()
        if all([bay.warehouse == bays[0].warehouse for bay in bays]):
            return bays[0].warehouse
        return None

    def clean(self):
        """Add list of bay IDs to cleaned data."""
        cleaned_data = super().clean()
        cleaned_data.pop(self.PRODUCT_NAME)
        cleaned_data.pop(self.STOCK_LEVEL)
        bays = self.cleaned_data[self.LOCATIONS][self.BAYS]
        if len(bays) == 0:
            bays = [self.warehouse.default_bay.bay_ID]
        cleaned_data[self.LOCATIONS][self.BAYS] = bays
        return cleaned_data

    def save(self):
        """Update product with new bays."""
        self.product.bays = self.cleaned_data[self.LOCATIONS][self.BAYS]

    def get_context_data(self, *args, **kwargs):
        """Return cotext for template."""
        context = super().get_context_data(*args, **kwargs)
        context["bays"] = [
            bay.name for bay in models.Bay.objects.filter(bay_ID__in=self.product.bays)
        ]
        return context


class LocationsFormSet(KwargFormSet):
    """Formset for updating the locations of all Products within a Range."""

    form = LocationsForm
