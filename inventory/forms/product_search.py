"""Forms for product search page."""

from django import forms
from django.db.models import Count

from inventory import models

from .widgets import HorizontalRadio


class ProductSearchForm(forms.Form):
    """Product search form."""

    ranges = []

    EXCLUDE_EOL = "exclude_eol"
    INCLUDE_EOL = "include_eol"
    ONLY_EOL = "only_eol"
    END_OF_LINE_DEFAULT = EXCLUDE_EOL
    END_OF_LINE_CHOICES = (
        (EXCLUDE_EOL, "Exclude EOL"),
        (INCLUDE_EOL, "Include EOL"),
        (ONLY_EOL, "Only EOL"),
    )

    search_term = forms.CharField(required=False)
    end_of_line = forms.ChoiceField(
        widget=HorizontalRadio(),
        choices=END_OF_LINE_CHOICES,
        required=False,
        label="End of Line",
        help_text="Hide End of Line Ranges",
    )
    supplier = forms.ModelChoiceField(
        queryset=models.Supplier.objects.filter(active=True), required=False
    )

    def save(self):
        """Search for product ranges matching the search parameters."""
        products = self._filter_products(self._query_products())
        range_queryset = self._filter_ranges(self._query_ranges(products))
        self.ranges = range_queryset.order_by("name").annotate(
            variation_count=Count("products")
        )

    def _query_products(self):
        end_of_line = self.get_eol()
        if search_term := self.cleaned_data["search_term"]:
            qs = models.BaseProduct.objects.text_search(
                search_term, end_of_line=end_of_line
            )
        else:
            qs = models.Product.objects.filter(is_end_of_line=end_of_line)
        qs = qs.variations().select_related("product_range", "supplier")
        if end_of_line is not None:
            qs = qs.filter(product_range__is_end_of_line=end_of_line)
        qs = qs.prefetch_related(
            "variation_option_values", "variation_option_values__variation_option"
        ).order_by("product_range__name")
        return qs

    def _query_ranges(self, products):
        range_pks = (
            products.values_list("product_range", flat=True).order_by().distinct()
        )
        return models.ProductRange.ranges.filter(
            pk__in=range_pks, status=models.ProductRange.COMPLETE
        )

    def _filter_ranges(self, ranges):
        ranges = self._filter_end_of_line(ranges)
        return ranges

    def _filter_products(self, products):
        products = self._filter_supplier(products)
        return products

    def _filter_end_of_line(self, ranges):
        eol = self.cleaned_data.get("end_of_line")
        if eol == self.EXCLUDE_EOL:
            ranges = ranges.filter(is_end_of_line=False)
        elif eol == self.ONLY_EOL:
            ranges = ranges.filter(is_end_of_line=True)
        return ranges

    def get_eol(self):
        """Return a filter value for the is_end_of_line attribute."""
        eol = self.cleaned_data.get("end_of_line")
        if eol == self.EXCLUDE_EOL:
            return False
        elif eol == self.ONLY_EOL:
            return True
        else:
            return None

    def _filter_supplier(self, products):
        if self.cleaned_data.get("supplier"):
            products = products.filter(supplier=self.cleaned_data["supplier"])
        return products
