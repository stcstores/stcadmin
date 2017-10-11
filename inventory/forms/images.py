from django import forms


class ImagesForm(forms.Form):
    product_ids = forms.CharField(widget=forms.HiddenInput)
    images = forms.ImageField(
        widget=forms.ClearableFileInput(
            attrs={'multiple': True, 'accept': '.jpg, .png'}))
