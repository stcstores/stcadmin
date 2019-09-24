"""Forms for updating product locations."""

from django import forms

from inventory.cloud_commerce_updater import ProductUpdater
from product_editor.editor_manager import ProductEditorBase
from product_editor.forms.fields import WarehouseBayField
from stcadmin.forms import KwargFormSet


class LocationsForm(forms.Form):
    """Form for changing the Warehouse Bays associated with a product."""

    PRODUCT_NAME = "product_name"
    LOCATION = "locations"
    WAREHOUSE = ProductEditorBase.WAREHOUSE
    BAYS = ProductEditorBase.BAYS

    def __init__(self, *args, **kwargs):
        """Add fields to form."""
        self.product = kwargs.pop("product")
        self.user = kwargs.pop("user")
        super().__init__(*args, **kwargs)
        self.fields[self.LOCATION] = WarehouseBayField(inline=True)
        self.cleaned_data = {}
        self.initial.update(self.get_initial())

    def get_initial(self):
        """Return initial data."""
        initial = {}
        bays = self.product.bays.all()
        warehouses = list(set([bay.warehouse for bay in bays]))
        if len(warehouses) > 1:
            raise ValueError(f"Product {self.product.SKU} is in multiple warehouses.")
        elif len(warehouses) == 1:
            initial[self.LOCATION] = {
                self.WAREHOUSE: warehouses[0].id,
                self.BAYS: [bay.id for bay in bays],
            }
        return initial

    def clean(self):
        """Add list of bay IDs to cleaned data."""
        cleaned_data = super().clean()
        cleaned_data[self.BAYS] = cleaned_data[self.LOCATION][self.BAYS]
        return cleaned_data

    def save(self):
        """Update product with new bays."""
        updater = ProductUpdater(self.product, self.user)
        updater.set_bays(self.cleaned_data[self.BAYS])


class LocationsFormSet(KwargFormSet):
    """Formset for updating the locations of all Products within a Range."""

    form = LocationsForm
