from django.views.generic.base import TemplateView
from home.views import UserInGroupMixin
from inventory import models


class InventoryUserMixin(UserInGroupMixin):
    groups = ['inventory']


class NewProductView(InventoryUserMixin, TemplateView):
    template_name = 'inventory/new_product/new_product.html'


class SKUGeneratorView(InventoryUserMixin, TemplateView):
    template_name = 'inventory/sku_generator.html'


class PriceCalculator(InventoryUserMixin, TemplateView):
    template_name = 'inventory/price_calculator.html'

    def get_context_data(self, *args, **kwargs):
        context_data = super().get_context_data(*args, **kwargs)
        context_data['countries'] = models.DestinationCountry.objects.all()
        context_data['package_types'] = models.PackageType.objects.all()
        return context_data
