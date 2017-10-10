from django import forms
from django.forms import formset_factory


class ImagesForm(forms.Form):
    product_id = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'product_id'}))
    product_name = forms.CharField(
        disabled=True,
        required=False,
        widget=forms.TextInput(attrs={'size': 200, 'class': 'product_title'}))
    images = forms.TextInput()


ImagesFormSet = formset_factory(ImagesForm, extra=0)
