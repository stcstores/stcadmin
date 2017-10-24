from django import forms


class ImagesForm(forms.Form):
    product_ids = forms.CharField(widget=forms.HiddenInput)
    cloud_commerce_images = forms.ImageField(
        required=False,
        label='Cloud Commerce Images',
        widget=forms.ClearableFileInput(
            attrs={'multiple': True, 'accept': '.jpg, .png'}))
    stcadmin_images = forms.ImageField(
        required=False,
        label='STC Admin Images',
        widget=forms.ClearableFileInput(
            attrs={'multiple': True, 'accept': '.jpg, .png'}))
