"""Views for the Stock Check app."""

import json

from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView

from home.views import UserInGroupMixin
from inventory.models import ProductBayLink
from linnworks.models.stock_manager import StockManager
from stock_check import models


class StockCheckUserMixin(UserInGroupMixin):
    """View mixin to ensure user has permissions for the Stock Check app."""

    groups = ["stock_check"]


class AjaxOpenOrders(StockCheckUserMixin, View):
    """Return the number of open orders for all products in a bay."""

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        """Return HTTP response.Return the number of open orders for products in a bay as JSON."""
        bay_products = (
            ProductBayLink.objects.filter(bay__pk=self.kwargs.get("bay_ID"))
            .select_related("product")
            .values_list("product", flat=True)
            .order_by()
            .distinct()
        )
        order_count = self.count_products(bay_products)
        return JsonResponse(order_count)

    def count_products(self, products):
        """Return a dict containing the number of open orders for product IDs."""
        order_count = {}
        for product in products:
            stock_level_info = StockManager.stock_level_info(product.sku)
            order_count[product.pk] = stock_level_info.in_orders
        return order_count


class ProductSearch(TemplateView):
    """Search for products and get current stock level details."""

    template_name = "stock_check/product_search.html"

    # def get_context_data(self, *args, **kwargs):
    #     """Return context for template."""
    #     context = super().get_context_data(*args, **kwargs)
    #     search_term = self.request.GET.get("search_term", None)
    #     if search_term:
    #         context["search_term"] = search_term
    #         context["products"] = []
    #         for result in CCAPI.search_products(search_term):
    #             cc_product = cc_products.get_product(result.variation_id)
    #             product = models.Product.objects.get(product_id=cc_product.id)
    #             product.cc_product = cc_product
    #             context["products"].append(product)
    #         context["products"].sort(key=lambda x: x.cc_product.full_name)
    #     return context


class Bay(TemplateView):
    """Show current Products and Stock levels for Bay."""

    template_name = "stock_check/bay.html"

    def get_context_data(self, *args, **kwargs):
        """Return context for template."""
        context = super().get_context_data(*args, **kwargs)
        bay = get_object_or_404(models.Bay, id=self.kwargs.get("bay_pk"))
        context["bay"] = bay
        products = (
            ProductBayLink.objects.filter(bay=bay)
            .select_related("product", "product__product_range")
            .values_list("product")
            .order_by("product_range__name")
            .distinct()
        )
        context["products"] = products
        return context


class UpdateStockCheckLevel(StockCheckUserMixin, View):
    """Allows the quantity of a Product in a Bay to be updated via AJAX."""

    @method_decorator(csrf_exempt)
    def dispatch(self, request):
        """Update ProductBay model with new stock number."""
        request_data = json.loads(self.request.body)
        product_id = int(request_data["product_id"])
        bay_pk = int(request_data["bay_pk"])
        level = int(request_data["level"]) if request_data["level"] else None
        product_bay = get_object_or_404(
            models.ProductBay, product__pk=product_id, bay__pk=bay_pk
        )
        product_bay.stock_level = level
        product_bay.save()
        return HttpResponse('{"status": "ok"}')
