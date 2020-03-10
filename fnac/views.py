"""Views for the fnac app."""

from django.shortcuts import reverse
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from fnac import forms, models
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


class MissingPriceSize(FnacUserMixin, FormView):
    """View for displaying products that cannot be listed on FNAC because they do not have a price."""

    template_name = "fnac/missing_prices.html"
    form_class = forms.MissingPriceSizeFormset

    def form_valid(self, formset):
        """Save forms and redirect."""
        if formset.is_valid():
            for form in formset:
                form.save()
        return super().form_valid(formset)

    def get_success_url(self):
        """Return the URL to redirect to if forms submission is successful."""
        return reverse("fnac:index")
