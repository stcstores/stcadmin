"""Views for the fnac app."""

from django.views.generic.base import TemplateView

from fnac import models
from home.views import UserInGroupMixin


class FnacUserMixin(UserInGroupMixin):
    """View mixin to ensure user is in the print audit group."""

    groups = ["fnac"]


class Index(FnacUserMixin, TemplateView):
    """Index view for the fnac app."""

    template_name = "fnac/index.html"


class MissingInventoryInfo(FnacUserMixin, TemplateView):
    """View for displaying products that are not listed on FNAC due to missing inventory info."""

    template_name = "fnac/missing_inventory_info.html"

    def get_context_data(self, *args, **kwargs):
        """Return template context."""
        context = super().get_context_data(*args, **kwargs)
        context[
            "products"
        ] = models.FnacProduct.to_create.missing_inventory_information()
        return context
