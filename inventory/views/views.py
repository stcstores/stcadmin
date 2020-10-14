"""Miscellaneous views for inventory."""


from django.views.generic.base import TemplateView

from home.views import UserInGroupMixin


class InventoryUserMixin(UserInGroupMixin):
    """Mixin to validate user in in inventory group."""

    groups = ["inventory"]


class SKUGeneratorView(InventoryUserMixin, TemplateView):
    """View for SKU Generator page."""

    template_name = "inventory/sku_generator.html"
