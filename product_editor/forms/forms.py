"""Forms for new products."""

from ccapi import CCAPI
from django import forms
from product_editor.editor_manager import ProductEditorBase
from stcadmin.forms import KwargFormSet

from . import fields


class ProductForm(forms.Form, ProductEditorBase):
    """Base class for new product forms."""

    field_size = 50


class BasicInfo(ProductForm):
    """Form for product attributes that stay the same between variations."""

    def __init__(self, *args, **kwargs):
        """Get fields for form."""
        self.options = CCAPI.get_product_options()
        super().__init__(*args, **kwargs)
        self.fields[self.TITLE] = fields.Title()
        self.fields[self.DEPARTMENT] = fields.Department()
        self.fields[self.DESCRIPTION] = fields.Description()
        self.fields[self.AMAZON_BULLET_POINTS] = fields.AmazonBulletPoints()
        self.fields[self.AMAZON_SEARCH_TERMS] = fields.AmazonSearchTerms()


class ProductInfo(ProductForm):
    """Form for product attributes that vary between variations."""

    def __init__(self, *args, **kwargs):
        """Get Product option data and set fields."""
        self.options = CCAPI.get_product_options()
        super().__init__(*args, **kwargs)
        self.get_fields()

    def get_fields(self):
        """Set form fields."""
        self.fields[self.BARCODE] = fields.Barcode()
        self.fields[self.PURCHASE_PRICE] = fields.PurchasePrice()
        self.fields[self.PRICE] = fields.VATPrice()
        self.fields[self.RETAIL_PRICE] = fields.RetailPrice()
        self.fields[self.STOCK_LEVEL] = fields.StockLevel()
        self.fields[self.LOCATION] = fields.WarehouseBayField()
        self.fields[self.SUPPLIER] = fields.Supplier()
        self.fields[self.SUPPLIER_SKU] = fields.SupplierSKU()
        self.fields[self.WEIGHT] = fields.Weight()
        self.fields[self.DIMENSIONS] = fields.Dimensions()
        self.fields[self.PACKAGE_TYPE] = fields.PackageType()
        self.fields[self.BRAND] = fields.Brand(
            choices=fields.Brand.get_choices(
                "Brand", self.options, self.initial.get(self.BRAND, None)
            )
        )
        self.fields[self.MANUFACTURER] = fields.Manufacturer(
            choices=fields.Brand.get_choices(
                "Manufacturer", self.options, self.initial.get(self.MANUFACTURER, None)
            )
        )
        self.fields[self.GENDER] = fields.Gender()
        self.fields[self.PRODUCT_ID] = forms.CharField(
            widget=forms.HiddenInput(), required=False
        )


class BaseOptionsForm(ProductForm):
    """Base class for forms dealing with Product Options."""

    def __init__(self, *args, **kwargs):
        """Get choices for Product Option fields."""
        self.option_data = kwargs.pop("option_data", CCAPI.get_product_options())
        super().__init__(*args, **kwargs)
        self._get_fields()

    def _get_options(self):
        return [
            (option.option_name, [value.value for value in option])
            for option in self.option_data
            if option.exclusions["tesco"] is False
        ]

    def _get_choice_values(self, option_name, values):
        if option_name in self.initial:
            new_values = [v for v in self.initial[option_name] if v not in values]
            values += new_values
        return values

    def _get_fields(self):
        for option_name, values in self._get_options():
            choices = [("", "")] + [
                (v, v) for v in self._get_choice_values(option_name, values)
            ]
            self.fields[option_name] = self.field_class(
                label=option_name, choices=choices
            )


class VariationOptions(BaseOptionsForm):
    """Form to select variations for new variation products."""

    field_class = fields.VariationOptions

    def clean(self):
        """Check correct number of variations are supplied for each field."""
        cleaned_data = super().clean()
        cleaned_data = cleaned_data.copy()
        if all([len(v) == 0 for k, v in cleaned_data.items()]):
            self.add_error(None, "At least one variation option must be used.")
        for key, value in cleaned_data.items():
            if len(value) == 1:
                self.add_error(
                    key,
                    ("At least two values must be supplied " "for any used option."),
                )
        return cleaned_data


class ListingOptions(BaseOptionsForm):
    """Form to set Product Options for listings for single items."""

    field_class = fields.ListingOption


class BaseVariationForm(ProductForm):
    """Base class for forms handeling variations."""

    def __init__(self, *args, **kwargs):
        """Set initial data and create fields."""
        self.variation_options = kwargs.pop("variation_options")
        self.existing_data = kwargs.pop("existing_data")
        super().__init__(*args, **kwargs)
        self._update_initial()
        self.get_fields()
        self.order_fields(list(self.variation_options.keys()))

    def _update_initial(self):
        if self.existing_data is not None:
            for variation in self.existing_data:
                correct_form = all(
                    [
                        variation.get(key) == self.variation_options.get(key)
                        for key in self.variation_options
                    ]
                )
                if correct_form:
                    self.initial.update(variation)

    def _get_choice_values(self, option_name, values):
        if option_name in self.initial:
            if self.initial[option_name] not in values:
                values.append(self.initial[option_name])
        return values


class UnusedVariations(BaseVariationForm):
    """Form to mark non existant variations as unused."""

    def get_fields(self):
        """Set form fields."""
        self.fields[self.USED] = forms.BooleanField(initial=True, required=False)
        self.fields[self.PRODUCT_ID] = forms.CharField(
            widget=forms.HiddenInput(), required=False
        )
        for option_name, value in self.variation_options.items():
            self.fields[option_name] = forms.CharField(
                max_length=255, initial=value, widget=forms.HiddenInput()
            )

    def clean(self):
        """Ensure existing products are not marked unused."""
        data = super().clean()
        if data[self.PRODUCT_ID]:
            data[self.USED] = True
        return data


class VariationInfo(BaseVariationForm):
    """Form to set required information for variation."""

    def __init__(self, *args, **kwargs):
        """Set choices for choice fields."""
        choices = kwargs.pop("choices")
        self.supplier_choices = choices["supplier"]
        self.package_type_choices = choices["package_type"]
        self.options = kwargs.pop("options")
        super().__init__(*args, **kwargs)

    def get_fields(self):
        """Set form fields."""
        ProductInfo.get_fields(self)
        for option_name, value in self.variation_options.items():
            self.fields[option_name] = forms.CharField(
                max_length=255, initial=value, widget=forms.HiddenInput()
            )


class VariationListingOptions(BaseVariationForm):
    """Form to set listing Product Options for variations."""

    def __init__(self, *args, **kwargs):
        """Get option values."""
        self.option_values = kwargs.pop("option_values")
        super().__init__(*args, **kwargs)

    def get_fields(self):
        """Set form fields."""
        for option_name, value in self.variation_options.items():
            self.fields[option_name] = forms.CharField(
                max_length=255, initial=value, widget=forms.HiddenInput()
            )
        for option_name, values in self.option_values.items():
            if option_name not in self.variation_options:
                choices = [("", "")] + [
                    (v, v) for v in self._get_choice_values(option_name, values)
                ]
                self.fields[option_name] = fields.ListingOption(
                    choices=choices, label=option_name
                )


class BaseVariationFormSet(KwargFormSet):
    """Base formset for variation forms."""

    def __init__(self, *args, **kwargs):
        """Configure kwargs for forms in formset."""
        self.kwargs = kwargs
        kwarg_update = self._update_form_kwargs()
        for form_kwargs in kwargs["form_kwargs"]:
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
            "supplier": fields.Supplier.get_choices(),
            "package_type": fields.PackageType.get_choices(),
        }
        options = CCAPI.get_product_options()
        return {"choices": choices, "options": options}


class VariationListingOptionsSet(BaseVariationFormSet):
    """Formset for setting listing Product Options for new products."""

    form = VariationListingOptions

    def _update_form_kwargs(self):
        option_data = CCAPI.get_product_options()
        option_values = {
            option.option_name: [value.value for value in option]
            for option in option_data
            if option.exclusions["tesco"] is False
        }
        return {"option_values": option_values}
