"""Views for the Stock Check app."""

import json

import cc_products
from ccapi import CCAPI
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView

from home.views import UserInGroupMixin
from stock_check import models


class StockCheckUserMixin(UserInGroupMixin):
    """View mixin to ensure user has permissions for the Stock Check app."""

    groups = ["stock_check"]


class AjaxOpenOrders(StockCheckUserMixin, View):
    """Return the number of open orders for all products in a bay."""

    @method_decorator(csrf_exempt)
    def dispatch(self, request, bay_id):
        """Return HTTP response.

        Return the number of open orders for products in a bay as JSON.
        """
        product_ids = self.product_ids(bay_id)
        orders = self.orders()
        order_count = self.count_products(product_ids, orders)
        response_text = json.dumps(order_count)
        return HttpResponse(response_text)

    def product_ids(self, bay_id):
        """Return a list of IDs of products in the bay with ID bay_id."""
        bay = models.Bay.objects.get(bay_id=bay_id)
        products = bay.product_set.all()
        product_ids = [product.product_id for product in products]
        return product_ids

    def orders(self):
        """Return all the current open orders."""
        open_orders = CCAPI.get_orders_for_dispatch(order_type=0, number_of_days=0)
        issue_orders = CCAPI.get_orders_for_dispatch(issue_orders=True)
        return open_orders + issue_orders

    def count_products(self, product_ids, orders):
        """Return a dict containing the number of open orders for product IDs."""
        order_count = {str(product_id): 0 for product_id in product_ids}
        for order in orders:
            for product in order.products:
                if str(product.product_id) in order_count:
                    order_count[product.product_id] += product.quantity
        return order_count


class ProductSearch(TemplateView):
    """Search for products and get current stock level details."""

    template_name = "stock_check/product_search.html"

    def get_context_data(self, *args, **kwargs):
        """Return context for template."""
        context = super().get_context_data(*args, **kwargs)
        search_term = self.request.GET.get("search_term", None)
        if search_term:
            context["search_term"] = search_term
            context["products"] = []
            for result in CCAPI.search_products(search_term):
                cc_product = cc_products.get_product(result.variation_id)
                product = models.Product.objects.get(product_id=cc_product.id)
                product.cc_product = cc_product
                context["products"].append(product)
            context["products"].sort(key=lambda x: x.cc_product.full_name)
        return context


class Warehouses(StockCheckUserMixin, TemplateView):
    """View provides an index of Warehouses."""

    template_name = "stock_check/warehouses.html"

    def get_context_data(self, *args, **kwargs):
        """Return context for template."""
        context = super().get_context_data(*args, **kwargs)
        context["warehouses"] = models.Warehouse.objects.all()
        return context


class Warehouse(StockCheckUserMixin, TemplateView):
    """View provides an index of Bays for a given Warehouse."""

    template_name = "stock_check/warehouse.html"

    def get_context_data(self, *args, **kwargs):
        """Return context for template."""
        context = super().get_context_data(*args, **kwargs)
        warehouse_id = self.kwargs.get("warehouse_id")
        warehouse = get_object_or_404(models.Warehouse, warehouse_id=warehouse_id)
        context["warehouse"] = warehouse
        context["bays"] = list(
            models.Bay.non_default.filter(warehouse=warehouse).all().order_by("name")
        )
        context["bays"].insert(0, warehouse.default_bay)
        return context


class Bay(TemplateView):
    """Show current Products and Stock levels for Bay."""

    template_name = "stock_check/bay.html"

    def get_context_data(self, *args, **kwargs):
        """Return context for template."""
        context = super().get_context_data(*args, **kwargs)
        bay_id = self.kwargs.get("bay_id")
        context["bay"] = get_object_or_404(models.Bay, bay_id=bay_id)
        products = context["bay"].product_set.all()
        context["products"] = []
        for product in products:
            product.cc_product = cc_products.get_product(product.product_id)
            context["products"].append(product)
        context["products"].sort(key=lambda x: x.cc_product.full_name)
        return context


class UpdateStockCheckLevel(StockCheckUserMixin, View):
    """Allows the quantity of a Product in a Bay to be updated via AJAX."""

    @method_decorator(csrf_exempt)
    def dispatch(self, request):
        """Update ProductBay model with new stock number."""
        request_data = json.loads(self.request.body)
        product_id = int(request_data["product_id"])
        bay_id = int(request_data["bay_id"])
        level = int(request_data["level"]) if request_data["level"] else None
        product_bay = get_object_or_404(
            models.ProductBay, product__id=product_id, bay__id=bay_id
        )
        product_bay.stock_level = level
        product_bay.save()
        return HttpResponse('{"status": "ok"}')
