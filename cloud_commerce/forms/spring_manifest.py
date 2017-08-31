from django import forms


class SpringManifestForm(forms.Form):

    MANIFEST_TYPES = (
        ('standard', 'Standard'), ('tracked', 'Tracked'), ('parcel', 'Parcel'))

    manifest_type = forms.ChoiceField(
        required=True,
        label='Manifest Type',
        choices=MANIFEST_TYPES,
        widget=forms.RadioSelect())
