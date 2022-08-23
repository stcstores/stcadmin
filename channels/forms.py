"""Forms for the Channels app."""

from django import forms
from django.db.models import Count
from django.forms.models import inlineformset_factory
from django_select2.forms import ModelSelect2TagWidget

from channels import models
from inventory.forms.fields import Description
from inventory.models import BaseProduct, ProductRange


class TagWidget(ModelSelect2TagWidget):
    """Widget for selecting tags for Shopify products."""

    queryset = models.shopify_models.ShopifyTag.objects.all()
    search_fields = ("name__icontains",)

    def build_attrs(self, base_attrs, extra_attrs=None):
        """Add select2's tag attributes."""
        default_attrs = {
            "data-minimum-input-length": 1,
            "data-tags": "true",
            "data-token-separators": '[","]',
        }
        default_attrs.update(base_attrs)
        return super().build_attrs(default_attrs, extra_attrs=extra_attrs)

    def label_from_instance(self, obj):
        """Return the string representation of the object."""
        return obj.name

    def value_from_datadict(self, data, files, name):
        """Create missing values."""
        values = super().value_from_datadict(data, files, name)
        tags = []
        for value in values:
            if value.isnumeric():
                tag = models.shopify_models.ShopifyTag.objects.get(id=int(value))
            else:
                tag, _ = models.shopify_models.ShopifyTag.objects.get_or_create(
                    name=value.lower()
                )
            tags.append(tag)
        return tags


class ShopifyListingForm(forms.ModelForm):
    """Form for Shopify listings."""

    class Meta:
        """Metaclass for ShopifyListingForm."""

        model = models.shopify_models.ShopifyListing
        exclude = ("product_id",)
        field_classes = {"description": Description}
        widgets = {
            "product_range": forms.HiddenInput(),
            "tags": TagWidget(),
        }


class ShopifyVariationForm(forms.ModelForm):
    """Form for shopify variations."""

    class Meta:
        """Metaclass for ShopifyVariationForm."""

        model = models.shopify_models.ShopifyVariation
        exclude = ("variant_id", "inventory_item_id")
        widgets = {"listing": forms.HiddenInput(), "product": forms.HiddenInput()}


VariationFormset = inlineformset_factory(
    models.shopify_models.ShopifyListing,
    models.shopify_models.ShopifyVariation,
    form=ShopifyVariationForm,
    extra=0,
    can_delete=False,
)


class ProductSearchForm(forms.Form):
    """Product search form."""

    ALL = "all"
    CREATED = "created"
    NOT_CREATED = "not created"
    LISTED_FILTER_DEFAULT = ALL
    LISTED_FILTER_CHOICES = (
        (ALL, "All Products"),
        (CREATED, "With Listing"),
        (NOT_CREATED, "Without Listing"),
    )

    search_term = forms.CharField(required=False)
    listed = forms.ChoiceField(
        choices=LISTED_FILTER_CHOICES,
        required=False,
        label="Has Listing",
    )

    def save(self):
        """Search for product ranges matching the search parameters."""
        products = self._filter_products(self._query_products())
        range_queryset = self._filter_ranges(self._query_ranges(products))
        self.ranges = range_queryset.order_by("name").annotate(
            variation_count=Count("products")
        )

    def _query_products(self):
        search_term = self.cleaned_data["search_term"]
        if search_term:
            qs = BaseProduct.objects.text_search(search_term)
        else:
            qs = BaseProduct.objects.all()
        qs = qs.variations().active()
        qs = qs.variations().select_related("product_range", "supplier")
        qs = qs.prefetch_related(
            "variation_option_values",
            "variation_option_values__variation_option",
            "shopify_listing",
        ).order_by("product_range__name")
        return qs

    def _query_ranges(self, products):
        range_pks = (
            products.values_list("product_range", flat=True).order_by().distinct()
        )
        return ProductRange.ranges.filter(
            pk__in=range_pks, status=ProductRange.COMPLETE
        )

    def _filter_ranges(self, ranges):
        ranges = self._filter_listed(ranges)
        return ranges

    def _filter_products(self, products):
        return products

    def _filter_listed(self, ranges):
        listed = self.cleaned_data.get("listed")
        if listed == self.CREATED:
            ranges = ranges.filter(shopify_listing__isnull=False)
        elif listed == self.NOT_CREATED:
            ranges = ranges.filter(shopify_listing__isnull=True)
        return ranges
