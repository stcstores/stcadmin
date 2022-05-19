"""Model admin for price_calculator app."""

from adminsortable2.admin import SortableAdminMixin
from django.contrib import admin

from price_calculator import models


@admin.register(models.CountryChannelFee)
class CountryChannelFeeAdmin(admin.ModelAdmin):
    """Model admin for the CountryChannelFee model."""

    fields = ("country", "min_channel_fee")
    list_display = ("country", "min_channel_fee")
    list_editable = ("min_channel_fee",)


@admin.register(models.ChannelFee)
class ChannelFeeAdmin(admin.ModelAdmin):
    """Model admin for the ChannelFee model."""

    exclude = ()
    list_display = ("__str__", "name", "fee_percentage", "country", "ordering")
    list_display_links = ("__str__",)
    list_editable = ("name", "fee_percentage", "country", "ordering")
    search_fields = ("name",)
    list_filter = ("country",)
    list_select_related = ("country",)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Limit the country drop down to countries with shipping methods."""
        if db_field.name == "country":
            kwargs["queryset"] = models.Country.objects.filter(
                id__in=models.ShippingMethod.objects.values_list("country", flat=True)
            )
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(models.Channel)
class ChannelAdmin(admin.ModelAdmin):
    """Model admin for the Channel model."""

    fields = ("name", "ordering")
    list_display = ("__str__", "name", "ordering")
    list_display_links = ("__str__",)
    list_editable = ("name", "ordering")


@admin.register(models.ProductType)
class ProductTypeAdmin(admin.ModelAdmin):
    """Model admin for ProductType model."""

    fields = ("name", "package_types")
    list_display = ("id", "name", "package_type_string")
    list_editable = ("name",)
    search_fields = ("name",)


@admin.register(models.ShippingMethod)
class ShippingMethodeAdmin(admin.ModelAdmin):
    """Model admin for ShippingMethod model."""

    fields = (
        "name",
        "country",
        "shipping_service",
        "product_type",
        "channel",
        "min_weight",
        "max_weight",
        "min_price",
        "max_price",
        "vat_rates",
        "active",
    )
    list_display = (
        "id",
        "name",
        "country",
        "shipping_service",
        "min_weight",
        "max_weight",
        "min_price",
        "max_price",
        "active",
    )
    list_editable = (
        "name",
        "country",
        "shipping_service",
        "min_weight",
        "max_weight",
        "min_price",
        "max_price",
        "active",
    )
    list_filter = (
        ("product_type", admin.RelatedOnlyFieldListFilter),
        ("country", admin.RelatedOnlyFieldListFilter),
        ("shipping_service", admin.RelatedOnlyFieldListFilter),
        ("vat_rates", admin.RelatedOnlyFieldListFilter),
        "active",
    )
    search_fields = ("name",)


@admin.register(models.VATRate)
class VATRateAdmin(SortableAdminMixin, admin.ModelAdmin):
    """Model admin for VATRate model."""

    fields = ("name", "cc_id", "percentage")
    list_display = ("__str__", "name", "cc_id", "percentage")
    list_display_links = ("__str__",)
    list_editable = ("name", "cc_id", "percentage")
    search_fields = ("name",)
