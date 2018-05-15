"""Forms for new products."""

from ccapi import CCAPI
from django import forms

from stcadmin.forms import KwargFormSet

from . import fields


class ProductForm(forms.Form):
    """Base class for new product forms."""

    field_size = 50


class BasicInfo(ProductForm):
    """Form to set necessary information about new products."""

    def __init__(self, *args, **kwargs):
        """Get fields for form."""
        self.options = CCAPI.get_product_options()
        super().__init__(*args, **kwargs)
        self.fields['title'] = fields.Title()
        self.fields['description'] = fields.Description()
        self.fields['amazon_bullet_points'] = fields.AmazonBulletPoints()
        self.fields['amazon_search_terms'] = fields.AmazonSearchTerms()


class ProductInfo(ProductForm):
    def __init__(self, *args, **kwargs):
        """Get fields for form."""
        self.options = CCAPI.get_product_options()
        super().__init__(*args, **kwargs)
        self.fields['barcode'] = fields.Barcode()
        self.fields['purchase_price'] = fields.PurchasePrice()
        self.fields['price'] = fields.VATPrice()
        self.fields['retail_price'] = fields.RetailPrice()
        self.fields['stock_level'] = fields.StockLevel()
        self.fields['department'] = fields.DepartmentBayField()
        self.fields['supplier'] = fields.Supplier()
        self.fields['supplier_sku'] = fields.SupplierSKU()
        self.fields['weight'] = fields.Weight()
        self.fields['dimensions'] = fields.Dimensions()
        self.fields['package_type'] = fields.PackageType()
        self.fields['brand'] = fields.Brand(
            choices=fields.Brand.get_choices(
                'Brand', self.options, self.initial.get('brand', None)))
        self.fields['manufacturer'] = fields.Manufacturer(
            choices=fields.Brand.get_choices(
                'Manufacturer', self.options,
                self.initial.get('manufacturer', None)))
        self.fields['gender'] = fields.Gender()


class BaseOptionsForm(ProductForm):
    """Base class for forms dealing with Product Options."""

    def __init__(self, *args, **kwargs):
        """Get choices for Product Option fields."""
        self.option_data = kwargs.pop(
            'option_data', CCAPI.get_product_options())
        super().__init__(*args, **kwargs)
        self._get_fields()

    def _get_options(self):
        return [
            (option.option_name, [value.value for value in option]) for option
            in self.option_data if option.exclusions['tesco'] is False]

    def _get_choice_values(self, option_name, values):
        if option_name in self.initial:
            new_values = [
                v for v in self.initial[option_name] if v not in values]
            values += new_values
        return values

    def _get_fields(self):
        for option_name, values in self._get_options():
            choices = [('', '')] + [
                (v, v) for v in self._get_choice_values(option_name, values)]
            self.fields[option_name] = self.field_class(
                label=option_name, choices=choices)


class VariationOptions(BaseOptionsForm):
    """Form to select variations for new variation products."""

    field_class = fields.VariationOptions

    def clean(self):
        """Check correct number of variations are supplied for each field."""
        cleaned_data = super().clean()
        cleaned_data = cleaned_data.copy()
        if all([len(v) == 0 for k, v in cleaned_data.items()]):
            self.add_error(None, 'At least one variation option must be used.')
        for key, value in cleaned_data.items():
            if len(value) == 1:
                self.add_error(
                    key, (
                        'At least two values must be supplied '
                        'for any used option.'))
        return cleaned_data


class ListingOptions(BaseOptionsForm):
    """Form to set Product Options for listings for single items."""

    field_class = fields.ListingOption


class BaseVariationForm(ProductForm):
    """Base class for forms handeling variations."""

    def __init__(self, *args, **kwargs):
        """Set initial data and create fields."""
        self.variation_options = kwargs.pop('variation_options')
        self.existing_data = kwargs.pop('existing_data')
        super().__init__(*args, **kwargs)
        self._update_initial()
        self._get_fields()
        self.order_fields(list(self.variation_options.keys()))

    def _update_initial(self):
        if self.existing_data is not None:
            for variation in self.existing_data:
                correct_form = all([
                    variation.get(key) == self.variation_options.get(key)
                    for key in self.variation_options])
                if correct_form:
                    self.initial.update(variation)

    def _get_choice_values(self, option_name, values):
        if option_name in self.initial:
            if self.initial[option_name] not in values:
                values.append(self.initial[option_name])
        return values


class UnusedVariations(BaseVariationForm):
    """Form to mark non existant variations as unused."""

    def _get_fields(self):
        self.fields['used'] = forms.BooleanField(initial=True, required=False)
        for option_name, value in self.variation_options.items():
            self.fields[option_name] = forms.CharField(
                max_length=255, initial=value, widget=forms.HiddenInput())


class VariationInfo(BaseVariationForm):
    """Form to set required information for variation."""

    def __init__(self, *args, **kwargs):
        """Set choices for choice fields."""
        choices = kwargs.pop('choices')
        self.supplier_choices = choices['supplier']
        self.package_type_choices = choices['package_type']
        self.department = kwargs.pop('department')
        self.options = kwargs.pop('options')
        super().__init__(*args, **kwargs)

    def _get_fields(self):
        self.fields['barcode'] = fields.Barcode()
        self.fields['purchase_price'] = fields.PurchasePrice()
        self.fields['price'] = fields.VATPrice()
        self.fields['retail_price'] = fields.RetailPrice()
        self.fields['stock_level'] = fields.StockLevel()
        self.fields['location'] = fields.Location(department=self.department)
        self.fields['supplier'] = fields.Supplier(
            choices=self.supplier_choices)
        self.fields['supplier_sku'] = fields.SupplierSKU()
        self.fields['weight'] = fields.Weight()
        self.fields['dimensions'] = fields.Dimensions()
        self.fields['package_type'] = fields.PackageType(
            choices=self.package_type_choices)
        self.fields['brand'] = fields.Brand(
            choices=fields.Brand.get_choices(
                'Brand', self.options, self.initial.get('brand', None)))
        self.fields['manufacturer'] = fields.Manufacturer(
            choices=fields.Brand.get_choices(
                'Manufacturer', self.options,
                self.initial.get('manufacturer', None)))
        self.fields['gender'] = fields.Gender()
        for option_name, value in self.variation_options.items():
            self.fields[option_name] = forms.CharField(
                max_length=255, initial=value, widget=forms.HiddenInput())


class VariationListingOptions(BaseVariationForm):
    """Form to set listing Product Options for variations."""

    def __init__(self, *args, **kwargs):
        """Get option values."""
        self.option_values = kwargs.pop('option_values')
        super().__init__(*args, **kwargs)

    def _get_fields(self):
        for option_name, value in self.variation_options.items():
            self.fields[option_name] = forms.CharField(
                max_length=255, initial=value, widget=forms.HiddenInput())
        for option_name, values in self.option_values.items():
            if option_name not in self.variation_options:
                choices = [('', '')] + [
                    (v, v) for v in self._get_choice_values(
                        option_name, values)]
                self.fields[option_name] = fields.ListingOption(
                    choices=choices, label=option_name)


class BaseVariationFormSet(KwargFormSet):
    """Base formset for variation forms."""

    def __init__(self, *args, **kwargs):
        """Configure kwargs for forms in formset."""
        self.kwargs = kwargs
        kwarg_update = self._update_form_kwargs()
        for form_kwargs in kwargs['form_kwargs']:
            form_kwargs.update(kwarg_update)
        super().__init__(*args, **kwargs)

    def _update_form_kwargs(self):
        return {}


class UnusedVariationsFormSet(BaseVariationFormSet):
    """Formset marking non existant variations as unused."""

    form = UnusedVariations


class VariationInfoSet(BaseVariationFormSet):
    """Formset for setting necessary information for variations."""

    form = VariationInfo

    def _update_form_kwargs(self):
        choices = {
            'supplier': fields.Supplier.get_choices(),
            'package_type': fields.PackageType.get_choices()}
        options = CCAPI.get_product_options()
        return {
            'choices': choices, 'department': self.kwargs.pop('department'),
            'options': options}


class VariationListingOptionsSet(BaseVariationFormSet):
    """Formset for setting listing Product Options for new products."""

    form = VariationListingOptions

    def _update_form_kwargs(self):
        option_data = CCAPI.get_product_options()
        option_values = {
            option.option_name: [value.value for value in option] for option
            in option_data if option.exclusions['tesco'] is False}
        return {'option_values': option_values}
