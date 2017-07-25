from django import forms
from django.forms import formset_factory

from list_input import ListInput


class LocationsForm(forms.Form):
    product_id = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'product_id'}))
    product_name = forms.CharField(
        disabled=True,
        required=False,
        widget=forms.TextInput(attrs={'size': 200, 'class': 'product_title'}))
    locations = ListInput(required=True)


LocationsFormSet = formset_factory(LocationsForm, extra=0)
