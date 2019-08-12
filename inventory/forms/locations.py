"""Forms for updating product locations."""

from django import forms

from inventory import models
from inventory.cloud_commerce_updater import ProductUpdater
from product_editor.editor_manager import ProductEditorBase
from product_editor.forms.fields import WarehouseBayField
from stcadmin.forms import KwargFormSet


class LocationsForm(forms.Form):
    """Form for changing the Warehouse Bays associated with a product."""

    PRODUCT_NAME = "product_name"
    LOCATIONS = "locations"
    WAREHOUSE = ProductEditorBase.WAREHOUSE
    BAYS = ProductEditorBase.BAYS

    def __init__(self, *args, **kwargs):
        """Add fields to form."""
        self.product = kwargs.pop("product")
        super().__init__(*args, **kwargs)
        self.fields[self.LOCATIONS] = WarehouseBayField(inline=True)
        self.cleaned_data = {}
        self.initial.update(self.get_initial())

    def get_initial(self):
        """Return initial data."""
        initial = {}
        bays = self.product.bays.all()
        warehouses = list(set([bay.warehouse for bay in bays]))
        if len(warehouses) > 1:
            self.add_error(self.LOCATIONS, "Mixed warehouses.")
        elif len(warehouses) == 1:
            initial[self.LOCATIONS] = {
                self.WAREHOUSE: bays[0].warehouse.warehouse_ID,
                self.BAYS: [bay.bay_ID for bay in bays],
            }
        return initial

    def clean(self):
        """Add list of bay IDs to cleaned data."""
        cleaned_data = super().clean()
        cleaned_data[self.BAYS] = models.Bay.objects.filter(
            bay_ID__in=cleaned_data[self.LOCATIONS][self.BAYS]
        )
        return cleaned_data

    def save(self):
        """Update product with new bays."""
        updater = ProductUpdater(self.product, self.request.user)
        updater.set_bays(self.cleaned_data[self.BAYS])


class LocationsFormSet(KwargFormSet):
    """Formset for updating the locations of all Products within a Range."""

    form = LocationsForm
