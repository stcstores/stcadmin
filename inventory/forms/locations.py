"""Forms for updating product locations."""

from django import forms
from django_select2 import forms as s2forms

from inventory import models
from inventory.forms.fields import BayField


class LocationsForm(forms.Form):
    """Form for changing the Warehouse Bays associated with a product."""

    product_id = forms.CharField(max_length=255, widget=forms.HiddenInput)
    bays = BayField(required=False)

    def clean(self):
        """Add list of bay IDs to cleaned data."""
        cleaned_data = super().clean()
        return cleaned_data

    def save(self, user):
        """Update product with new bays."""
        product = models.Product.objects.get(id=self.cleaned_data["product_id"])
        models.ProductBayHistory.objects.set_product_bays(
            user=user,
            product=product,
            bays=self.cleaned_data["bays"],
        )


LocationsFormSet = forms.formset_factory(LocationsForm, extra=0)


class BayWidget(s2forms.ModelSelect2Widget):
    """Widget for selecting a bay."""

    search_fields = ["name__icontains"]

    def get_queryset(*args, **kwargs):
        """Return a queryset of bays."""
        return models.Bay.objects.all()


class BaySearchForm(forms.Form):
    """Form for selecting a bay to view the contents of."""

    bay = forms.ModelChoiceField(queryset=models.Bay.objects.all(), widget=BayWidget())
