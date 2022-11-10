"""View for updating Product Warehouse Bays."""

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from inventory import forms, models
from inventory.forms import LocationsFormSet
from linnworks.models import StockManager

from .views import InventoryUserMixin


class LocationFormView(InventoryUserMixin, FormView):
    """View for LocationsFormSet."""

    template_name = "inventory/product_range/locations.html"
    form_class = LocationsFormSet

    def get_initial(self):
        """Return initial form values."""
        self.product_range = get_object_or_404(
            models.ProductRange, pk=self.kwargs.get("range_pk")
        )
        self.products = self.product_range.products.active().simple()
        initial = []
        for product in self.products:
            bays = [bay_link.bay.id for bay_link in product.product_bay_links.all()]
            initial.append({"product_id": product.id, "bays": bays})
        return initial

    def form_valid(self, formset):
        """Update product bays."""
        for form in formset:
            form.save(user=self.request.user)
        messages.add_message(self.request, messages.SUCCESS, "Locations Updated")
        return redirect(self.get_success_url())

    def get_context_data(self, *args, **kwargs):
        """Get template context data."""
        context = super().get_context_data(*args, **kwargs)
        context["product_range"] = self.product_range
        context["formset"] = context["form"]
        products = self.product_range.products.variations()
        for i, form in enumerate(context["formset"]):
            form.product = self.products[i]
        if not self.product_range.is_end_of_line:
            product_skus = products.filter(is_end_of_line=False).values_list(
                "sku", flat=True
            )
            try:
                context["products_exist"] = StockManager.products_exist(*product_skus)
            except Exception:
                context["products_exist"] = None
        else:
            context["products_exist"] = None
        return context

    def get_success_url(self):
        """Return URL to redirect to after successful form submission."""
        return self.product_range.get_absolute_url()


class BaySearch(InventoryUserMixin, TemplateView):
    """View for finding the contents of a bay."""

    template_name = "inventory/bay_search.html"
    form_class = forms.BaySearchForm

    def get_context_data(self, *args, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(*args, **kwargs)
        if "bay" in self.request.GET:
            context["form"] = self.form_class(self.request.GET)
            bay = models.Bay.objects.get(id=int(self.request.GET["bay"]))
            product_ids = bay.product_bay_links.all().values_list("product", flat=True)
            context["products"] = [
                (product, self.get_other_bays(product, bay))
                for product in models.BaseProduct.objects.filter(id__in=product_ids)
            ]

        else:
            context["form"] = self.form_class()
        return context

    def get_other_bays(self, product, bay):
        """Return a list of other bays the product is in."""
        links = product.product_bay_links.exclude(bay=bay)
        return [link.bay for link in links]
