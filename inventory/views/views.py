from ccapi import CCAPI
from django.views.generic.base import TemplateView
from home.views import UserInGroupMixin


class InventoryUserMixin(UserInGroupMixin):
    groups = ['inventory']


class Index(InventoryUserMixin, TemplateView):
    template_name = 'inventory/index.html'


class ProductRange(InventoryUserMixin, TemplateView):
    template_name = 'inventory/product_range.html'

    def get_context_data(self, **kwargs):
        product_range = CCAPI.get_range(kwargs['range_id'])
        return {'product_range': product_range}
