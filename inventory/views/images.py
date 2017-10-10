from ccapi import CCAPI
from django.views.generic.base import TemplateView

from .views import InventoryUserMixin


class ImageFormView(InventoryUserMixin, TemplateView):

    template_name = 'inventory/images.html'

    def dispatch(self, *args, **kwargs):
        self.range_id = self.kwargs.get('range_id')
        self.product_range = CCAPI.get_range(self.range_id)
        self.products = self.product_range.products
        for product in self.products:
            product.images = product.get_images()
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['product_range'] = self.product_range
        context['products'] = self.products
        return context
