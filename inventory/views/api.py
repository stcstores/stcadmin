"""Views for AJAX requests."""

from django.http import HttpResponse, JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView

from inventory import models

from .views import InventoryUserMixin


@method_decorator(csrf_exempt, name="dispatch")
class GetNewSKUView(InventoryUserMixin, View):
    """Return new Product SKU."""

    def post(self, *args, **kwargs):
        """Return a new product SKU."""
        sku = models.new_product_sku()
        return HttpResponse(sku)


@method_decorator(csrf_exempt, name="dispatch")
class GetNewRangeSKUView(InventoryUserMixin, View):
    """Return new Product Range SKU."""

    def post(self, *args, **kwargs):
        """Process HTTP request."""
        sku = models.new_range_sku()
        return HttpResponse(sku)


class NewInstance(View):
    """Create a new instance of a model with only a name field."""

    def post(self, *args, **kwargs):
        """Process HTTP request."""
        name = self.request.POST["name"]
        instance = self.model_class(name=name)
        instance.save()
        return JsonResponse({"name": instance.name, "id": instance.pk})


@method_decorator(csrf_exempt, name="dispatch")
class NewBrand(InventoryUserMixin, NewInstance):
    """Create a new brand."""

    model_class = models.Brand


@method_decorator(csrf_exempt, name="dispatch")
class NewManufacturer(InventoryUserMixin, NewInstance):
    """Create a new manufacturer."""

    model_class = models.Manufacturer


@method_decorator(csrf_exempt, name="dispatch")
class NewSupplier(InventoryUserMixin, NewInstance):
    """Create a new supplier."""

    model_class = models.Supplier


@method_decorator(csrf_exempt, name="dispatch")
class VariationList(InventoryUserMixin, TemplateView):
    """Return the contents of the variation table for a range."""

    template_name = "inventory/product_search/variation_list.html"

    def get_context_data(self, *args, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(*args, **kwargs)
        product_range_id = self.kwargs["product_range_pk"]
        context["products"] = models.BaseProduct.objects.filter(
            product_range__id=product_range_id
        ).variations()
        return context
