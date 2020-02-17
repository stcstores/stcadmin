"""Variation Formset."""

from django import forms

from product_editor.forms import fields
from stcadmin.forms import KwargFormSet


class VariationForm(forms.Form):
    """Form for editing variation products."""

    ignore_options = [
        "Department",
        "Brand",
        "Manufacturer",
        "WooCategory1",
        "WooCategory2",
        "WooCategory3",
        "International Shipping",
        "Package Type",
        "Supplier",
        "Purchase Price",
        "Date Created",
        "Location",
        "Supplier SKU",
        "Amazon Bullets",
        "Amazon Search Terms",
        "Linn SKU",
        "Linn Title",
        "Retail Price",
    ]

    product_id = forms.CharField(widget=forms.HiddenInput)
    price = fields.VATPrice()
    purchase_price = fields.PurchasePrice()
    retail_price = fields.RetailPrice()
    weight = fields.Weight()

    def __init__(self, *args, **kwargs):
        """Configure form fields."""
        self.product = kwargs.pop("product")
        self.option_names = kwargs.pop("selected_options")
        self.options = kwargs.pop("options")
        self.options = {
            o: v for o, v in self.options.items() if o not in self.ignore_options
        }
        super().__init__(*args, **kwargs)
        for option_name, values in self.options.items():
            choices = [("", "")] + [
                (v, v) for v in self.get_choice_values(option_name, values)
            ]
            self.fields["opt_" + option_name] = fields.ListingOption(
                choices=choices, label=option_name
            )
        self.initial = self.get_initial()

    def get_initial(self):
        """Return initial values for form."""
        initial = {}
        initial["price"] = {
            "vat_rate": self.product.vat_rate,
            "ex_vat": self.product.price,
            "with_vat_price": None,
        }
        initial["weight"] = self.product.weight
        initial["purchase_price"] = self.product.purchase_price
        initial["retail_price"] = self.product.retail_price
        for option_name in self.option_names:
            value = self.product.options[option_name]
            if value is not None:
                initial["opt_" + option_name] = value
            else:
                initial["opt_" + option_name] = ""
        initial["product_id"] = self.product.id
        return initial

    def get_choice_values(self, option_name, values):
        """Return choices for option field."""
        if option_name in self.initial:
            if self.initial[option_name] not in values:
                values.append(self.initial[option_name])
        return values

    def save(self):
        """Update product."""
        data = self.cleaned_data
        self.product.vat_rate = data["price"]["vat_rate"]
        self.product.price = data["price"]["ex_vat"]
        self.product.weight = data["weight"]
        self.product.purchase_price = data["purchase_price"]
        self.product.retail_price = data["retail_price"]
        options = [key[4:] for key in data.keys() if key[:4] == "opt_"]
        for option in options:
            value = data["opt_" + option]
            self.product.options[option] = value


class VariationsFormSet(KwargFormSet):
    """Form set for editing all variations in a product range."""

    form = VariationForm
