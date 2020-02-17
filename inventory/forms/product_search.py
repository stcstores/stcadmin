"""Forms for product search page."""

from django import forms
from django.contrib.postgres.search import SearchVector

from inventory import models
from product_editor.forms import fields
from product_editor.forms.widgets import HorizontalRadio


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

    SEARCH_FIELDS = (
        "product_range__range_ID",
        "product_range__name",
        "product_range__SKU",
        "product_ID",
        "SKU",
        "supplier_SKU",
        "barcode",
    )

    search_term = forms.CharField(required=False)
    end_of_line = forms.ChoiceField(
        widget=HorizontalRadio(),
        choices=END_OF_LINE_CHOICES,
        required=False,
        label="End of Line",
        help_text="Hide End of Line Ranges",
    )
    department = fields.Department(required=False)
    supplier = fields.Supplier(required=False)
    show_hidden = forms.BooleanField(required=False)

    def save(self):
        """Search for product ranges matching the search parameters."""
        products = self._filter_products(self._query_products())
        product_ranges = self._filter_ranges(self._query_ranges(products))
        self.ranges = product_ranges

    def _query_products(self):
        if self.cleaned_data["search_term"]:
            return models.Product.objects.annotate(
                search=SearchVector(*self.SEARCH_FIELDS)
            ).filter(search=self.cleaned_data["search_term"])
        else:
            return models.Product.objects.all()

    def _query_ranges(self, products):
        range_IDs = (
            products.order_by().values_list("product_range", flat=True).distinct()
        )
        return models.ProductRange.objects.filter(pk__in=range_IDs).order_by("name")

    def _filter_ranges(self, ranges):
        ranges = self._filter_end_of_line(ranges)
        ranges = self._filter_department(ranges)
        ranges = self._filter_hidden(ranges)
        return ranges

    def _filter_products(self, products):
        products = self._filter_supplier(products)
        return products

    def _filter_end_of_line(self, ranges):
        eol = self.cleaned_data.get("end_of_line")
        if eol == self.EXCLUDE_EOL:
            ranges = ranges.filter(end_of_line=False)
        elif eol == self.ONLY_EOL:
            ranges = ranges.filter(end_of_line=True)
        return ranges

    def _filter_department(self, ranges):
        if self.cleaned_data.get("department"):
            ranges = ranges.filter(department=self.cleaned_data["department"])
        return ranges

    def _filter_supplier(self, products):
        if self.cleaned_data.get("supplier"):
            products = products.filter(supplier=self.cleaned_data["supplier"])
        return products

    def _filter_hidden(self, ranges):
        if not self.cleaned_data.get("show_hidden"):
            ranges = ranges.filter(hidden=False)
        return ranges
