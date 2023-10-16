"""Forms for product search page."""

from django import forms
from django.db.models import Count

from inventory import models


class ProductSearchForm(forms.Form):
    """Product search form."""

    ranges = []

    EXCLUDE_ARCHIVED = "exclude_archived"
    INCLUDE_ARCHIVED = "include_archived"
    ONLY_ARCHIVED = "only_archived"
    ARCHIVED_DEFAULT = EXCLUDE_ARCHIVED
    ARCHIVED_CHOICES = (
        (EXCLUDE_ARCHIVED, "Hide Archived"),
        (INCLUDE_ARCHIVED, "Show Archived"),
        (ONLY_ARCHIVED, "Only Archived"),
    )

    search_term = forms.CharField(required=False)
    archived = forms.ChoiceField(
        choices=ARCHIVED_CHOICES,
        required=False,
        label="Archived",
    )
    supplier = forms.ModelChoiceField(
        queryset=models.Supplier.objects.active(), required=False
    )

    def get_queryset(self):
        """Search for product ranges matching the search parameters."""
        products = self._filter_products(self._query_products())
        range_queryset = self._query_ranges(products)
        return range_queryset.order_by("name").annotate(
            variation_count=Count("products")
        )

    def _query_products(self):
        archived = self.get_archived()
        if search_term := self.cleaned_data["search_term"]:
            qs = models.BaseProduct.objects.text_search(search_term, archived=archived)
        else:
            qs = models.Product.objects.filter(is_archived=archived)
        qs = qs.variations().select_related("product_range", "supplier")
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

    def _filter_products(self, products):
        products = self._filter_supplier(products)
        return products

    def get_archived(self):
        """Return a filter value for the is_archived attribute."""
        archived = self.cleaned_data.get("archived")
        if archived == self.EXCLUDE_ARCHIVED:
            return False
        elif archived == self.ONLY_ARCHIVED:
            return True
        else:
            return None

    def _filter_supplier(self, products):
        if self.cleaned_data.get("supplier"):
            products = products.filter(supplier=self.cleaned_data["supplier"])
        return products
