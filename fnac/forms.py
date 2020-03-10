"""Forms for the fnac app."""

from django import forms

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
