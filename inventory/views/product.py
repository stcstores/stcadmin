"""View for Product page."""

from django.contrib import messages
from django.db import transaction
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import RedirectView, TemplateView
from django.views.generic.edit import FormView, UpdateView

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


class SetProductEndOfLine(InventoryUserMixin, FormView):
    """View for setting products as end of line."""

    form_class = forms.EndOfLineReasonForm
    template_name = "inventory/product_range/eol_product.html"

    def get_context_data(self, *args, **kwargs):
        """Return the product to set EOL."""
        context = super().get_context_data(*args, **kwargs)
        context["product"] = get_object_or_404(models.Product, pk=self.kwargs["pk"])
        return context

    def form_valid(self, form):
        """Set product end of line."""
        self.object = get_object_or_404(models.Product, pk=self.kwargs["pk"])
        success_url = self.get_success_url()
        reason = form.cleaned_data["end_of_line_reason"]
        self.object.set_end_of_line(reason=reason)
        return HttpResponseRedirect(success_url)

    def get_success_url(self):
        """Return the url to redirect to after form submission."""
        return reverse(
            "inventory:product_range", kwargs={"range_pk": self.object.product_range.pk}
        )


class ClearEndOfLine(InventoryUserMixin, RedirectView):
    """View for unsetting products End of Line."""

    def get_redirect_url(self, *args, **kwargs):
        """Clear product EOL status."""
        product_id = self.kwargs.get("pk")
        product = models.BaseProduct.objects.get(id=product_id)
        if product.is_end_of_line and not product.is_archived:
            product.is_end_of_line = False
            product.end_of_line_reason = None
            product.save()
        return reverse(
            "inventory:product_range", kwargs={"range_pk": product.product_range.pk}
        )


class SetProductRangeEndOfLine(InventoryUserMixin, FormView):
    """View for setting product ranges as end of line."""

    form_class = forms.EndOfLineReasonForm
    template_name = "inventory/product_range/eol_product_range.html"

    def get_context_data(self, *args, **kwargs):
        """Return the product to set EOL."""
        context = super().get_context_data(*args, **kwargs)
        context["product_range"] = get_object_or_404(
            models.ProductRange, pk=self.kwargs["pk"]
        )
        return context

    def form_valid(self, form):
        """Set product end of line."""
        self.object = get_object_or_404(models.ProductRange, pk=self.kwargs["pk"])
        success_url = self.get_success_url()
        reason = form.cleaned_data["end_of_line_reason"]
        with transaction.atomic():
            for product in self.object.products.all():
                product.set_end_of_line(reason=reason)
        return HttpResponseRedirect(success_url)

    def get_success_url(self):
        """Return the url to redirect to after form submission."""
        return reverse("inventory:product_range", kwargs={"range_pk": self.object.pk})
