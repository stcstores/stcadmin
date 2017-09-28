from ccapi import CCAPI
from django import forms
from stcadmin.forms import KwargFormSet

from .new_product import fields
from .new_product.fields import FormFields


class VariationForm(forms.Form):

    product_id = forms.CharField(widget=forms.HiddenInput)
    vat_rate = fields.VATRate()
    price = fields.Price()

    def __init__(self, *args, **kwargs):
        self.product = kwargs.pop('product')
        self.product = CCAPI.get_product(self.product.id)
        super().__init__(*args, **kwargs)
        self.option_names = [
            option.option_name for option in self.product.options]
        self.variation_fields = [
            field for field in FormFields.option_fields if
            field.name.replace('opt_', '') in self.option_names]
        for field in self.variation_fields:
            self.fields[field.name] = field(small=True)
        self.initial = self.get_initial()

    def get_initial(self):
        initial = {}
        initial['vat_rate'] = fields.VATRate.get_VAT_percentage(
            self.product.vat_rate_id)
        initial['price'] = self.product.base_price
        for option in self.product.options:
            initial['opt_' + option.option_name] = option.value.value
        initial['product_id'] = self.product.id
        return initial

    def save(self):
        data = self.cleaned_data
        product = CCAPI.get_product(data['product_id'])
        product.set_vat_rate(data['vat_rate'])
        product.set_base_price(data['price'])
        for option_field in self.variation_fields:
            value = data[option_field.name]
            if len(value) > 0:
                product.set_option_value(
                    option_field.label, value, create=True)


class VariationsFormSet(KwargFormSet):
    form = VariationForm
