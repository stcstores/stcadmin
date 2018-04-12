from ccapi import CCAPI
from django import forms

from inventory import models

from .new_product import fields
from .new_product.fields import Description, Title


class ProductRangeForm(forms.Form):
    end_of_line = forms.BooleanField(
        required=False,
        help_text=(
            'Ranges are maked as <b>end of line</b> if the entire range is'
            ' out of stock and unlikely to be re-ordered.'))


class DescriptionForm(forms.Form):
    title = Title()
    description = Description()
    amazon_bullets = fields.AmazonBulletPoints()
    search_terms = fields.AmazonSearchTerms()


class CreateBayForm(forms.Form):
    BACKUP = 'backup'
    PRIMARY = 'primary'
    BAY_TYPE_CHOICES = ((PRIMARY, 'Primary'), (BACKUP, 'Backup'))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['department'] = fields.Department(label='Department')
        self.fields['department'].help_text = (
            "The department to which the bay's contents belong.")

        self.fields['name'] = forms.CharField(max_length=255, required=True)
        self.fields['name'].help_text = 'The name of the bay to be created.'

        self.fields['bay_type'] = forms.ChoiceField(
            choices=self.BAY_TYPE_CHOICES, widget=forms.RadioSelect,
            required=True, initial=self.PRIMARY)
        self.fields['bay_type'].help_text = (
            'Is this a primary picking location or backup bay?')

        self.fields['location'] = fields.Department(label='Location')
        self.fields['location'].help_text = 'The physical location of the bay.'
        self.fields['location'].required = False

    def clean(self, *args, **kwargs):
        data = super().clean(*args, **kwargs)
        if data['bay_type'] == self.BACKUP:
            if not data['location']:
                self.add_error(
                    'location', 'Location is required for backup bays.')
                return
        if data['bay_type'] == self.PRIMARY:
            warehouse = models.Warehouse.objects.get(name=data['department'])
            data['bay_name'] = data['name']
        else:
            warehouse = models.Warehouse.objects.get(name=data['department'])
            data['bay_name'] = '{} Backup {} {}'.format(
                warehouse.abriviation, data['location'], data['name'])
        data['warehouse_id'] = warehouse.warehouse_id
        data['warehouse_name'] = warehouse.name
        if models.Bay.objects.filter(name=data['bay_name']).exists():
            self.add_error('name', 'Bay name already exists.')
        return data

    def save(self):
        warehouse_id = self.cleaned_data['warehouse_id']
        warehouse = models.Warehouse.objects.get(warehouse_id=warehouse_id)
        bay_name = self.cleaned_data['bay_name']
        bay_id = CCAPI.get_bay_id(bay_name, warehouse.name, create=True)
        self.bay = models.Bay(
            bay_id=bay_id, warehouse=warehouse, name=bay_name)
        self.bay.save()
