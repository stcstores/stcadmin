"""Miscellaneous views for inventory."""

from django.contrib import messages
from django.shortcuts import redirect, render
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from home.views import UserInGroupMixin
from inventory import forms


class InventoryUserMixin(UserInGroupMixin):
    """Mixin to validate user in in inventory group."""

    groups = ["inventory"]


class SKUGeneratorView(InventoryUserMixin, TemplateView):
    """View for SKU Generator page."""

    template_name = "inventory/sku_generator.html"


class CreateBayView(InventoryUserMixin, FormView):
    """View for Create Bay page."""

    form_class = forms.CreateBayForm
    template_name = "inventory/create_warehouse_bay.html"

    def form_valid(self, form):
        """Process form request and return HttpResponse."""
        form.save()
        messages.add_message(
            self.request, messages.SUCCESS, "Created bay {}".format(form.new_bay)
        )
        return redirect("inventory:create_warehouse_bay")


class ProductSearchView(InventoryUserMixin, FormView):
    """View for product search page."""

    template_name = "inventory/product_search/search_page.html"
    form_class = forms.ProductSearchForm

    def get_form_kwargs(self, *args, **kwargs):
        """Return the kwargs to be passed to the form."""
        kwargs = super().get_form_kwargs(*args, **kwargs)
        if "data" in kwargs:
            kwargs["data"] = kwargs["data"].copy()
            for key, value in kwargs["initial"].items():
                if key not in kwargs["data"]:
                    kwargs["data"][key] = value
        return kwargs

    def get_initial(self):
        """Return the initial values for the product search form."""
        initial = super().get_initial()
        initial["end_of_line"] = self.form_class.END_OF_LINE_DEFAULT
        initial["show_hidden"] = False
        return initial

    def form_valid(self, form):
        """Process form request and return HttpResponse."""
        form.save()
        return render(
            self.request,
            self.template_name,
            {"form": form, "product_ranges": form.ranges},
        )
