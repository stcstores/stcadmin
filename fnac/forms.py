"""Forms for the fnac app."""

from django import forms

from fnac import models


class MissingPricesForm(forms.ModelForm):
    """Form for setting prices to FnacProduct objects."""

    class Meta:
        """Meta class for MissingPricesForm."""

        model = models.FnacProduct
        fields = ["price"]

    price = forms.DecimalField(min_value=0, decimal_places=2, required=False)

    def clean_price(self):
        """Return the price as an integer."""
        price = self.cleaned_data.get("price")
        if price is not None:
            price = int(self.cleaned_data["price"] * 100)
        return price


class MissingPricesFormset(forms.BaseModelFormSet):
    """Formset for adding missing prices to FnacProduct objects."""

    def __init__(self, *args, **kwargs):
        """Set up formset."""
        super().__init__(*args, **kwargs)
        self.form = MissingPricesForm
        self.model = models.FnacProduct
        self.queryset = models.FnacProduct.objects.filter(price__isnull=True).order_by(
            "pk"
        )
        self.min_num = self.queryset.count()
        self.max_num = self.queryset.count()
        self.absolute_max = self.queryset.count()
        self.extra = 0
        self.can_order = False
        self.can_delete = False
        self.validate_max = False
        self.validate_min = False
