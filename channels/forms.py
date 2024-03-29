"""Forms for the Channels app."""

from django import forms
from django.db.models import Count
from django.forms.models import inlineformset_factory
from django_summernote.widgets import SummernoteInplaceWidget

from channels import models
from inventory.models import BaseProduct, ProductRange


class ShopifyListingForm(forms.ModelForm):
    """Form for Shopify listings."""

    class Meta:
        """Metaclass for ShopifyListingForm."""

        model = models.shopify_models.ShopifyListing
        exclude = ("product_id", "collections", "tags")
        widgets = {
            "product_range": forms.HiddenInput(),
            "description": SummernoteInplaceWidget,
        }


class ShopifyTagsForm(forms.ModelForm):
    """Form for Shopify listing tags."""

    class Meta:
        """Metaclass for ShopifyTagsForm."""

        model = models.shopify_models.ShopifyListing
        fields = ("tags",)


class ShopifyCollectionsForm(forms.ModelForm):
    """Form for Shopify listing collections."""

    class Meta:
        """Metaclass for ShopifyCollectionsForm."""

        model = models.shopify_models.ShopifyListing
        fields = ("collections",)


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
        products = self._query_products()
        range_queryset = self._filter_listed(self._query_ranges(products))
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
        qs = qs.select_related("product_range", "supplier")
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

    def _filter_listed(self, ranges):
        listed = self.cleaned_data.get("listed")
        if listed == self.CREATED:
            ranges = ranges.filter(shopify_listing__isnull=False)
        elif listed == self.NOT_CREATED:
            ranges = ranges.filter(shopify_listing__isnull=True)
        return ranges


class ShopifyTagForm(forms.ModelForm):
    """Form for Shopify tags."""

    class Meta:
        """Metaclass for ShopifyTagForm."""

        model = models.shopify_models.ShopifyTag
        fields = ("name",)
