from django import forms

from list_input import ListInput


class LocationsForm(forms.Form):
    location = ListInput(required=True)
