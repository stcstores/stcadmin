"""Miscellaneous views for inventory."""


from django.views.generic.base import TemplateView
from django.views.generic.list import ListView

from home.views import UserInGroupMixin
from inventory import forms


class InventoryUserMixin(UserInGroupMixin):
    """Mixin to validate user in in inventory group."""

    groups = ["inventory"]


class SKUGeneratorView(InventoryUserMixin, TemplateView):
    """View for SKU Generator page."""

    template_name = "inventory/sku_generator.html"


class ProductSearchView(InventoryUserMixin, ListView):
    """View for product search page."""

    template_name = "inventory/product_search/search_page.html"
    form_class = forms.ProductSearchForm
    paginate_by = 30
    orphans = 3

    def get(self, *args, **kwargs):
        """Instanciate the form."""
        self.form = self.form_class(self.request.GET, initial=self.get_initial())
        return super().get(*args, **kwargs)

    def get_queryset(self):
        """Return a queryset of orders based on GET data."""
        if self.form.is_valid():
            return self.form.get_queryset()
        return []

    def get_context_data(self, *args, **kwargs):
        """Return the template context."""
        context = super().get_context_data(*args, **kwargs)
        context["form"] = self.form
        context["page_range"] = self.get_page_range(context["paginator"])
        return context

    def get_page_range(self, paginator):
        """Return a list of pages to link to."""
        if paginator.num_pages < 11:
            return list(range(1, paginator.num_pages + 1))
        else:
            return list(range(1, 11)) + [paginator.num_pages]

    def get_initial(self):
        """Return the initial values for the product search form."""
        initial = {}
        initial["end_of_line"] = self.form_class.END_OF_LINE_DEFAULT
        initial["show_hidden"] = False
        return initial
