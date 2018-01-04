import json

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
    groups = ['stock_check']


class OpenOrderCheck(StockCheckUserMixin, TemplateView):

    def get_order_data(self):
        self.orders = CCAPI.get_orders_for_dispatch(
            order_type=0, number_of_days=4)
        self.orders += CCAPI.get_orders_for_dispatch(issue_orders=True)
        self.product_lookup = {}
        for order in self.orders:
            for product in order.products:
                product.pick_list_printed = order.is_pick_list_printed
                product_id = int(product.product_id)
                if product_id not in self.product_lookup:
                    self.product_lookup[product_id] = []
                self.product_lookup[product_id].append(product)

    def get_open_orders_for_product(self, product):
        product.printed = 0
        product.unprinted = 0
        if int(product.id) not in self.product_lookup:
            product.allocated = 0
            return
        for order_product in self.product_lookup[int(product.id)]:
            if order_product.pick_list_printed:
                product.printed += order_product.quantity
            else:
                product.unprinted += order_product.quantity
        product.allocated = product.printed + product.unprinted


class ProductSearch(OpenOrderCheck):
    template_name = 'stock_check/product_search.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        search_term = self.request.GET.get('search_term', None)
        if search_term:
            self.get_order_data()
            context['search_term'] = search_term
            context['products'] = []
            for result in CCAPI.search_products(search_term):
                cc_product = CCAPI.get_product(result.variation_id)
                product = models.Product.objects.get(product_id=cc_product.id)
                self.get_open_orders_for_product(cc_product)
                product.cc_product = cc_product
                context['products'].append(product)
        return context


class Warehouses(StockCheckUserMixin, TemplateView):
    template_name = 'stock_check/warehouses.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['warehouses'] = models.Warehouse.objects.all()
        return context


class Warehouse(StockCheckUserMixin, TemplateView):
    template_name = 'stock_check/warehouse.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        warehouse_id = self.kwargs.get('warehouse_id')
        context['warehouse'] = get_object_or_404(
            models.Warehouse, id=warehouse_id)
        context['bays'] = models.Bay.objects.filter(
            warehouse=context['warehouse'])
        return context


class Bay(OpenOrderCheck):
    template_name = 'stock_check/bay.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        self.get_order_data()
        bay_id = self.kwargs.get('bay_id')
        context['bay'] = get_object_or_404(models.Bay, id=bay_id)
        products = context['bay'].product_set.all()
        context['products'] = []
        for product in products:
            product.cc_product = models.get_cc_product_by_sku(product.sku)
            self.get_open_orders_for_product(product.cc_product)
            context['products'].append(product)
        return context


class UpdateStockCheckLevel(StockCheckUserMixin, View):

    @method_decorator(csrf_exempt)
    def dispatch(self, request):
        request_data = json.loads(self.request.body)
        product_id = int(request_data['product_id'])
        bay_id = int(request_data['bay_id'])
        level = int(request_data['level']) if request_data['level'] else None
        product_bay = get_object_or_404(
            models.ProductBay, product__id=product_id, bay__id=bay_id)
        product_bay.stock_level = level
        product_bay.save()
        return HttpResponse('{"status": "ok"}')
