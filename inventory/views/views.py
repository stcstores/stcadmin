from ccapi import CCAPI
from django.views.generic.base import TemplateView
from home.views import UserInGroupMixin


class InventoryUserMixin(UserInGroupMixin):
    groups = ['inventory']


class NewProductView(InventoryUserMixin, TemplateView):
    template_name = 'inventory/new_product/new_product.html'


class SKUGeneratorView(InventoryUserMixin, TemplateView):
    template_name = 'inventory/sku_generator.html'


class StockCheck(InventoryUserMixin, TemplateView):
    template_name = 'inventory/stock_check.html'

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        search_term = self.request.GET.get('search_term', None)
        if search_term:
            self.get_order_data()
            context['search_term'] = search_term
            context['products'] = [
                CCAPI.get_product(p.variation_id) for p in
                CCAPI.search_products(search_term)]
            for product in context['products']:
                self.get_open_orders_for_product(product)
        return context

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
