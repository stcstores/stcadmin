from django.views.generic.base import TemplateView
from home.views import UserInGroupMixin


class InventoryUserMixin(UserInGroupMixin):
    groups = ['inventory']


class Index(InventoryUserMixin, TemplateView):
    template_name = 'inventory/index.html'


class NewProduct(InventoryUserMixin, TemplateView):
    template_name = 'inventory/new_product/new_product.html'


class SKUGenerator(InventoryUserMixin, TemplateView):
    template_name = 'inventory/sku_generator.html'
