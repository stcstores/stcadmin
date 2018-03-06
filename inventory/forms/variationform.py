from django import forms
from stcadmin.forms import KwargFormSet

from .new_product import fields


class VariationForm(forms.Form):

    product_id = forms.CharField(widget=forms.HiddenInput)
    vat_rate = fields.VATRate()
    price = fields.Price()
    weight = fields.Weight()

    def __init__(self, *args, **kwargs):
        self.product = kwargs.pop('product')
        super().__init__(*args, **kwargs)
        self.option_names = list(self.product.options.names.keys())
        self.variation_fields = [
            field for field in fields.FormFields.option_fields if
            field.name.replace('opt_', '') in self.option_names]
        for field in self.variation_fields:
            self.fields[field.name] = field(small=True)
        self.initial = self.get_initial()

    def get_initial(self):
        initial = {}
        initial['vat_rate'] = self.product.vat_rate
        initial['price'] = self.product.price
        initial['weight'] = self.product.weight
        for option_name in self.option_names:
            value = self.product.options[option_name]
            if value is not None:
                initial['opt_' + option_name] = value
            else:
                initial['opt_' + option_name] = ''
        initial['product_id'] = self.product.id
        return initial

    def save(self):
        data = self.cleaned_data
        print(data)
        self.product.vat_rate = data['vat_rate']
        self.product.price = data['price']
        self.product.weight = data['weight']
        for field in self.variation_fields:
            value = data[field.name]
            self.product.options[field.name.replace('opt_', '')] = value


class VariationsFormSet(KwargFormSet):
    form = VariationForm
