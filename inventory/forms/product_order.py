"""Form for setting the order of products within a range."""

from django import forms
from django.shortcuts import get_object_or_404

from inventory import models
from stcadmin.forms import KwargFormSet


class ProductOrderForm(forms.Form):
    """Form for setting the order of products within a range."""

    product_ID = forms.CharField()
    range_order = forms.IntegerField()

    def __init__(self, *args, **kwargs):
        """Add product to the form."""
        self.product = kwargs.pop("product")
        super().__init__(*args, **kwargs)
        self.initial.update(self.get_initial())

    def get_initial(self):
        """Return initial data."""
        initial = {}
        initial["product_ID"] = self.product.product_ID
        initial["range_order"] = self.product.range_order
        return initial

    def save(self):
        """Update the order of products."""
        data = self.cleaned_data
        product = get_object_or_404(models.Product, product_ID=data["product_ID"])
        product.range_order = data["range_order"]
        product.save()


class ProductOrderFormSet(KwargFormSet):
    """Formset for updating the locations of all Products within a Range."""

    form = ProductOrderForm
