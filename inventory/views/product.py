"""View for Product page."""

from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView
from django.views.generic.edit import DeleteView, UpdateView

from inventory import forms, models

from .views import InventoryUserMixin


class EditProduct(InventoryUserMixin, UpdateView):
    """View for ProductForm."""

    template_name = "inventory/product_range/edit_product.html"
    model = models.Product
    form_class = forms.EditProductForm

    def get_form_kwargs(self):
        """Return form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def get_success_url(self):
        """Return URL to redirect to after successful form submission."""
        messages.add_message(self.request, messages.SUCCESS, "Product Updated")
        return reverse_lazy("inventory:edit_product", kwargs={"pk": self.object.pk})

    def get_context_data(self, *args, **kwargs):
        """Get template context data."""
        context = super().get_context_data(*args, **kwargs)
        form = context["form"]
        context["product"] = form.instance
        context["product_range"] = form.instance.product_range
        return context


class ViewProduct(InventoryUserMixin, TemplateView):
    """View for viewing information about a single variation."""

    template_name = "inventory/product_range/view_product.html"

    def get_context_data(self, *args, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(*args, **kwargs)
        product = get_object_or_404(models.BaseProduct, pk=self.kwargs["pk"])
        context["product"] = product
        context["product_range"] = product.product_range
        return context


class SetProductEndOfLine(InventoryUserMixin, DeleteView):
    """View for setting products as end of line."""

    template_name = "inventory/product_range/confirm_eol_product.html"

    def get_object(self):
        """Return the product to set EOL."""
        return get_object_or_404(models.Product, pk=self.kwargs["pk"])

    def form_valid(self, form):
        """Set product end of line."""
        success_url = self.get_success_url()
        self.object.set_end_of_line()
        return HttpResponseRedirect(success_url)

    def get_success_url(self):
        """Return the url to redirect to after form submission."""
        return reverse(
            "inventory:product_range", kwargs={"range_pk": self.object.product_range.pk}
        )


class SetProductRangeEndOfLine(InventoryUserMixin, DeleteView):
    """View for setting products as end of line."""

    template_name = "inventory/product_range/confirm_eol_product_range.html"

    def get_object(self):
        """Return the product to set EOL."""
        return get_object_or_404(models.ProductRange, pk=self.kwargs["pk"])

    def form_valid(self, form):
        """Set product end of line."""
        success_url = self.get_success_url()
        with transaction.atomic():
            for product in self.object.products.all():
                product.set_end_of_line()
        return HttpResponseRedirect(success_url)

    def get_success_url(self):
        """Return the url to redirect to after form submission."""
        return reverse("inventory:product_range", kwargs={"range_pk": self.object.pk})
