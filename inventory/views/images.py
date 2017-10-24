from ccapi import CCAPI
import json
from django.views.generic.edit import FormView
from inventory.forms import ImagesForm
from inventory.models import STCAdminImage
from .views import InventoryUserMixin
from django.core.urlresolvers import reverse_lazy
from django.views.generic.base import RedirectView
from django.shortcuts import get_object_or_404


class DeleteSTCAdminImage(InventoryUserMixin, RedirectView):

    def get_redirect_url(self, image_id):
        stcadmin_image = get_object_or_404(
            STCAdminImage, pk=image_id)
        range_id = stcadmin_image.range_id
        stcadmin_image.delete()
        return reverse_lazy(
                'inventory:images', kwargs={'range_id': range_id})


class ImageFormView(InventoryUserMixin, FormView):

    template_name = 'inventory/images.html'
    form_class = ImagesForm

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
        options = {
            o.option_name: {} for o in self.product_range.options if
            o.is_web_shop_select}
        for product in self.products:
            for o in product.options:
                if o.option_name in options:
                    value = o.value.value
                    if value in options[o.option_name]:
                        options[o.option_name][value].append(product.id)
                    else:
                        options[o.option_name][value] = [product.id]
        context['options'] = options
        context['stcadmin_images'] = STCAdminImage.objects.filter(
            range_id=self.range_id)
        return context

    def get_success_url(self):
        return reverse_lazy(
            'inventory:images', kwargs={'range_id': self.range_id})

    def form_valid(self, form):
        product_ids = json.loads(form.cleaned_data['product_ids'])
        cc_files = self.request.FILES.getlist('cloud_commerce_images')
        stcadmin_images = self.request.FILES.getlist('stcadmin_images')
        for image in cc_files:
            image_file = image
            r = CCAPI.upload_image(
                product_ids=product_ids, image_file=image_file)
            r.raise_for_status()
        for image in stcadmin_images:
            STCAdminImage(range_id=self.range_id, image=image).save()
        return super().form_valid(form)
