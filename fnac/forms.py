"""Forms for the fnac app."""

from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction

from fnac import models


class MissingPriceSizeForm(forms.ModelForm):
    """Form for setting prices to FnacProduct objects."""

    class Meta:
        """Meta class for MissingPricesForm."""

        model = models.FnacProduct
        fields = ["price", "french_size"]

    price = forms.DecimalField(min_value=0, decimal_places=2, required=False)
    french_size = forms.ModelChoiceField(models.Size.objects.all(), required=False)

    def clean_price(self):
        """Return the price as an integer."""
        price = self.cleaned_data.get("price")
        if price is not None:
            price = int(self.cleaned_data["price"] * 100)
        return price


class MissingPriceSizeFormset(forms.BaseModelFormSet):
    """Formset for adding missing prices to FnacProduct objects."""

    def __init__(self, *args, **kwargs):
        """Set up formset."""
        super().__init__(*args, **kwargs)
        self.form = MissingPriceSizeForm
        self.model = models.FnacProduct
        self.queryset = (
            models.FnacProduct.objects.size_invalid()
            | models.FnacProduct.objects.missing_price()
        )
        self.min_num = self.queryset.count()
        self.max_num = self.queryset.count()
        self.absolute_max = self.queryset.count()
        self.extra = 0
        self.can_order = False
        self.can_delete = False
        self.validate_max = False
        self.validate_min = False


class MissingCategoryForm(forms.ModelForm):
    """Form for setting product categories."""

    class Meta:
        """Meta clas for MissingCategoryForm."""

        model = models.FnacRange
        fields = ["category"]


class MissingCategoryFormset(forms.BaseModelFormSet):
    """Formset for adding missing categories to FnacRange objects."""

    def __init__(self, *args, **kwargs):
        """Set up formset."""
        super().__init__(*args, **kwargs)
        self.form = MissingCategoryForm
        self.model = models.FnacRange
        self.queryset = models.FnacRange.objects.missing_category()
        self.min_num = self.queryset.count()
        self.max_num = self.queryset.count()
        self.absolute_max = self.queryset.count()
        self.extra = 0
        self.can_order = False
        self.can_delete = False
        self.validate_max = False
        self.validate_min = False


class TranslationsForm(forms.Form):
    """Form for adding translations."""

    translations = forms.CharField(widget=forms.Textarea())

    def clean_translations(self):
        """Prevent empty form submissions."""
        text = self.cleaned_data.get("translations")
        try:
            translations = [
                self._parse_row(row) for row in text.strip().split("¬")[1:] if row
            ]
        except Exception as e:
            raise ValidationError(f"Error parsing translation text: {e}.")
        if len(translations) == 0:
            raise ValidationError("No translations found.")
        return translations

    def _parse_row(self, row_text):
        split = row_text.split("\t")
        sku = self._read_sku(split[0])
        name = self._read_name(split[1])
        colour = self._read_colour(split[2])
        description = self._read_description(split[3:])
        try:
            product = models.FnacProduct.objects.get(sku=sku)
        except models.FnacProduct.DoesNotExist:
            raise ValidationError(f"No product with SKU {sku} exists.")
        return models.Translation(
            product=product, name=name, colour=colour, description=description
        )

    @transaction.atomic
    def save(self):
        """Save the translations."""
        for translation in self.cleaned_data["translations"]:
            translation.save()

    def _read_sku(self, text):
        return text.strip().replace(" ", "")

    def _read_name(self, text):
        return text.strip()

    def _read_colour(self, text):
        colour = text.strip()
        if colour == "Aucun":
            return ""
        return colour

    def _read_description(self, lines):
        return "".join([_.strip() for _ in lines if _])
