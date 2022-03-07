"""Forms for inventory app."""


from django import forms
from django.db import transaction

from inventory import models
from inventory.forms import fields as inventory_fields
from stcadmin.forms import KwargFormSet


class ProductRangeForm(forms.Form):
    """Form for editing a Product Range."""

    end_of_line = forms.BooleanField(
        required=False,
        help_text=(
            "Ranges are marked as <b>end of line</b> if the entire range is"
            " out of stock and unlikely to be re-ordered."
        ),
    )


class CreateRangeForm(forms.ModelForm):
    """Form for editing attributes that are the same across a range."""

    class Meta:
        """Meta for CreateRangeForm."""

        model = models.ProductRange
        exclude = ["end_of_line", "hidden", "status"]
        field_classes = {
            "name": inventory_fields.Title,
            "description": inventory_fields.Description,
            "amazon_search_terms": inventory_fields.AmazonSearchTerms,
            "amazon_bullet_points": inventory_fields.AmazonBulletPoints,
        }
        widgets = {"managed_by": forms.HiddenInput}

    sku = forms.CharField(required=False, widget=forms.HiddenInput)

    def clean(self, *args, **kwargs):
        """Format amazon list strings."""
        cleaned_data = super().clean(*args, **kwargs)
        if "amazon_bullets" in cleaned_data:
            cleaned_data["amazon_bullets"] = self.format_amazon_list(
                cleaned_data["amazon_bullets"]
            )
        if "search_terms" in cleaned_data:
            cleaned_data["search_terms"] = self.format_amazon_list(
                cleaned_data["search_terms"]
            )
        cleaned_data["sku"] = models.new_range_sku()
        return cleaned_data

    def format_amazon_list(self, amazon_list_json):
        """Return a formatted amazon list string."""
        return "|".join(amazon_list_json)


class InitialProductForm(forms.ModelForm):
    """Form for setting initial product attributes."""

    class Meta:
        """Meta for InitialProductForm."""

        model = models.Product
        exclude = (
            "end_of_line",
            "gender",
            "range_order",
        )
        field_classes = {
            # "barcode": inventory_fields.Barcode,
            # "purchase_price": inventory_fields.PurchasePrice,
            # "retail_price": inventory_fields.RetailPrice,
            # "vat_rate": inventory_fields.VATRateField,
            # "stock_level": inventory_fields.StockLevel,
            # "bay": inventory_fields.BayField,
            # "weight_grans": inventory_fields.Weight,
            # "brand": inventory_fields.Brand,
            # "manufacturer": inventory_fields.Manufacturer,
            # "package_type": inventory_fields.PackageType,
        }
        widgets = {"product_range": forms.HiddenInput, "sku": forms.HiddenInput}

        field_order = (
            "barcode",
            "purchase_prce",
            "retail_price",
            "vat_rate",
            "stock_level",
            "bay",
            "weight_grams",
            "length_mm",
            "height_mm",
            "width_mm",
            "dimensions",
            "package_type",
            "hs_code",
            "brand",
            "manufacturer",
        )

    sku = forms.CharField(required=False, widget=forms.HiddenInput)

    def clean(self, *args, **kwargs):
        """Return cleaned form data."""
        cleaned_data = super().clean(*args, **kwargs)
        cleaned_data["sku"] = models.new_product_sku()
        return cleaned_data


class SetupVariationsForm(forms.Form):
    """Setup variaion product options for a new product."""

    variations = forms.CharField()

    def __init__(self, *args, **kwargs):
        """Add fields."""
        super().__init__(*args, **kwargs)
        for variation_option in models.VariationOption.objects.all():
            self.fields[str(variation_option.pk)] = inventory_fields.VariationOptions(
                required=False,
                variation_option=variation_option,
                label=variation_option.name,
            )


class ProductForm(forms.ModelForm):
    """Form for editing indivdual Products."""

    class Meta:
        """Meta for InitialProductForm."""

        model = models.Product
        exclude = ("end_of_line", "gender", "range_order", "sku")
        field_classes = {
            # "barcode": inventory_fields.Barcode,
            # "purchase_price": inventory_fields.PurchasePrice,
            # "retail_price": inventory_fields.RetailPrice,
            # "vat_rate": inventory_fields.VATRateField,
            # "stock_level": inventory_fields.StockLevel,
            # "bay": inventory_fields.BayField,
            # "weight_grans": inventory_fields.Weight,
            # "brand": inventory_fields.Brand,
            # "manufacturer": inventory_fields.Manufacturer,
            # "package_type": inventory_fields.PackageType,
        }
        widgets = {
            "product_range": forms.HiddenInput,
        }

        field_order = (
            "barcode",
            "purchase_prce",
            "retail_price",
            "vat_rate",
            "stock_level",
            "bay",
            "weight_grams",
            "length_mm",
            "height_mm",
            "width_mm",
            "dimensions",
            "package_type",
            "hs_code",
            "brand",
            "manufacturer",
        )


class ProductFormset(KwargFormSet):
    """Formset for updating the locations of all Products within a Range."""

    form = ProductForm


class ImagesForm(forms.Form):
    """Form for adding product images."""

    product_ids = forms.CharField(widget=forms.HiddenInput)
    cloud_commerce_images = forms.ImageField(
        required=False,
        label="Cloud Commerce Images",
        widget=forms.ClearableFileInput(
            attrs={"multiple": True, "accept": ".jpg, .png"}
        ),
    )


class AddProductOption(forms.Form):
    """Add a new variation product option to a partial product range."""

    def __init__(self, *args, **kwargs):
        """Instanciate the form."""
        self.edit = kwargs.pop("edit")
        self.variation = kwargs.pop("variation")
        self.user = kwargs.pop("user")
        self.product_range = self.edit.partial_product_range
        super().__init__(*args, **kwargs)
        self.add_fields()

    def add_fields(self):
        """Add fields to the form."""
        self.fields["option"] = inventory_fields.SelectProductOption(
            product_range=self.product_range
        )
        for option_ID, name in self.fields["option"].choices:
            if not option_ID:
                continue
            self.fields[f"values_{option_ID}"] = inventory_fields.VariationOptions(
                product_option=models.ProductOption.objects.get(pk=option_ID),
                product_range=self.product_range,
                label=name,
                required=False,
            )

    def clean(self):
        """Ensure a new product option cannot be selected with fewer than two values."""
        cleaned_data = super().clean()
        if "option" in cleaned_data:
            values_field_name = f"values_{cleaned_data['option'].pk}"
            cleaned_data["values"] = cleaned_data[values_field_name]
            if self.variation is True and len(cleaned_data["values"]) < 2:
                self.add_error(
                    values_field_name,
                    "At least two variation options must be selected for each dropdown.",
                )
        return cleaned_data

    @transaction.atomic
    def save(self):
        """Save changes to the database."""
        pass
        # product_option = self.cleaned_data["option"]
        # product_option_values = self.cleaned_data["values"]
        # updater = PartialRangeUpdater(self.product_range, self.user)
        # if self.variation is True:
        #     updater.add_variation_product_option(product_option)
        # else:
        #     updater.add_listing_product_option(product_option)
        # for value in product_option_values:
        #     self.edit.product_option_values.add(value)


class SetProductOptionValues(forms.Form):
    """Form for adding values for a new product option to a product."""

    def __init__(self, *args, **kwargs):
        """Set up form fields."""
        self.edit = kwargs.pop("edit")
        self.product_range = kwargs.pop("product_range")
        self.product = kwargs.pop("product")
        kwargs["initial"] = self.get_initial()
        super().__init__(*args, **kwargs)
        self.fields["product_ID"] = forms.CharField(
            widget=forms.HiddenInput, required=True
        )
        self.options = self.product_range.product_options.all()
        self.variation_options = self.product_range.variation_options()
        self.listing_options = self.product_range.listing_options()
        for option in self.variation_options:
            self.add_option_field(option, True)
        for option in self.listing_options:
            self.add_option_field(option, False)

    def add_option_field(self, option, variation):
        """Add a product option field to the form."""
        name = f"option_{option.name}"
        self.fields[name] = inventory_fields.PartialProductOptionValueSelect(
            edit=self.edit, product_option=option
        )
        if variation is True:
            option_link = models.PartialProductRangeSelectedOption.objects.get(
                product_range=self.product_range, product_option=option
            )
            if option_link.pre_existing is True:
                self.fields[name].widget.attrs["disabled"] = True

    def clean(self):
        """Validate the form."""
        cleaned_data = super().clean()
        for option in self.options:
            name = f"option_{option.name}"
            if name not in cleaned_data or not cleaned_data[name]:
                cleaned_data[name] = ""
                self.add_error(
                    f"option_{option.name}", "Product option value cannot be empty."
                )
        return cleaned_data

    def variation(self):
        """Return a dict of submitted product option values."""
        variation = {}
        for option in self.variation_options:
            name = f"option_{option.name}"
            variation[name] = self.cleaned_data.get(name)
        return variation

    def get_initial(self):
        """Return the initial values for a product for the formset."""
        initial = {"product_ID": self.product.id}
        for product_option in self.product_range.product_options.all():
            name = f"option_{product_option.name}"
            value = self.get_product_option_value(self.product, product_option)
            if value:
                initial[name] = value
        return initial

    def get_product_option_value(self, product, product_option):
        """Return the initial product option value."""
        value = None
        try:
            value = models.PartialProductOptionValueLink.objects.get(
                product=self.product,
                product_option_value__product_option=product_option,
            ).product_option_value

        except models.PartialProductOptionValueLink.DoesNotExist:
            if product_option in self.product_range.listing_options():
                value = self.get_avaliable_option(product, product_option)
        return value

    def get_avaliable_option(self, product, product_option):
        """Return the only available listing option if possible, otherwise None."""
        values = self.edit.product_option_values.filter(product_option=product_option)
        if values.count() == 1:
            return values[0]


class SetProductOptionValuesFormset(KwargFormSet):
    """Formset for adding values for a new product option to a range."""

    form = SetProductOptionValues

    def clean(self):
        """Validate the formset."""
        for form in self.forms:
            variation = form.variation()
            for otherform in (_ for _ in self.forms if _ != form):
                if variation == otherform.variation():
                    form.add_error(
                        None, "This variation is not unique within the Product Range."
                    )
        self.multiple_values_for_variation_options()
        return super().clean()

    def multiple_values_for_variation_options(self):
        """Add an error if a variation option only has one value."""
        variation = self.forms[0].variation()
        for key in variation.keys():
            if all(
                (form.variation().get(key) == variation[key] for form in self.forms)
            ):
                for form in self.forms:
                    form.add_error(
                        key,
                        "Every variation cannot have the same value for a drop down. "
                        "Should this be a listing option?",
                    )
                return

    @transaction.atomic
    def save(self):
        """Update the variation product options for a product range."""
        models.PartialProductOptionValueLink.objects.filter(
            product__product_range=self.forms[0].product_range
        ).delete()
        for form in self.forms:
            product = models.PartialProduct.objects.get(
                id=form.cleaned_data["product_ID"]
            )
            for option in form.options:
                models.PartialProductOptionValueLink(
                    product=product,
                    product_option_value=form.cleaned_data[f"option_{option.name}"],
                ).save()


class AddProductOptionValuesForm(forms.Form):
    """Form for adding product option values to a partial product edit."""

    def __init__(self, *args, **kwargs):
        """Add fields."""
        self.edit = kwargs.pop("edit")
        self.product_option = kwargs.pop("product_option")
        super().__init__(*args, **kwargs)
        self.fields["values"] = inventory_fields.VariationOptions(
            product_option=self.product_option,
            product_range=self.edit.partial_product_range,
            label=self.product_option.name,
        )

    def save(self):
        """Add product option values to the produt edit."""
        for value in self.cleaned_data["values"]:
            self.edit.product_option_values.add(value)
