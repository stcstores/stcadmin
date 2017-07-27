from django import forms
from django.forms import formset_factory

from list_input import ListInput


class ImagesForm(forms.Form):
    product_id = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'product_id'}))
    product_name = forms.CharField(
        disabled=True,
        required=False,
        widget=forms.TextInput(attrs={'size': 200, 'class': 'product_title'}))
    stock_level = forms.CharField(required=False)
    locations = ListInput(required=True)
    images = forms.ImageField()


ImagesFormSet = formset_factory(ImagesForm, extra=0)
