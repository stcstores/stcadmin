"""Forms for updating product locations."""

from django import forms

from product_editor.editor_manager import ProductEditorBase
from product_editor.forms.fields import Location
from stcadmin.forms import KwargFormSet


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
        self.fields[self.LOCATIONS] = Location()
        self.cleaned_data = {}
        self.initial.update(self.get_initial())

    def get_initial(self):
        """Return initial data."""
        initial = {}
        initial[self.PRODUCT_ID] = self.product.id
        initial[self.PRODUCT_NAME] = self.product.full_name
        initial[self.STOCK_LEVEL] = self.product.stock_level
        initial[self.LOCATIONS] = self.product.bays
        return initial

    def clean(self):
        """Add list of bay IDs to cleaned data."""
        cleaned_data = super().clean()
        cleaned_data.pop(self.PRODUCT_NAME)
        cleaned_data.pop(self.STOCK_LEVEL)
        return cleaned_data

    def save(self):
        """Update product with new bays."""
        self.product.bays = self.cleaned_data[self.LOCATIONS]


class LocationsFormSet(KwargFormSet):
    """Formset for updating the locations of all Products within a Range."""

    form = LocationsForm
