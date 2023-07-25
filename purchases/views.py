"""Views for the purchases app."""

from django.views.generic import ListView, TemplateView

from home.views import UserInGroupMixin
from inventory.models import BaseProduct
from purchases import forms


class PurchasesUserMixin(UserInGroupMixin):
    """Mixin to validate user in in purchases group."""

    groups = ["purchases", "purchase_manager"]


class PurchaseManagerUserMixin(UserInGroupMixin):
    """Mixin to validate user in in purchase_manager group."""

    groups = ["purchase_manager"]


class ProductSearch(PurchasesUserMixin, TemplateView):
    """View for searching for products to purchase."""

    template_name = "purchases/product_search.html"

    def get_context_data(self, *args, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(*args, **kwargs)
        context["form"] = forms.ProductSearchForm()
        return context


class ProductSearchResults(PurchasesUserMixin, ListView):
    """AJAX view for displaying product search results."""

    model = BaseProduct
    paginate_by = 50
    template_name = "purchases/product_search_results.html"

    def get_queryset(self):
        """Return product queryset."""
        form = forms.ProductSearchForm(self.request.GET)
        return form.get_queryset()
