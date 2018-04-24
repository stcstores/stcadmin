"""Views for handeling Product Images."""

import json

from ccapi import CCAPI
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.base import RedirectView
from django.views.generic.edit import FormView

from inventory.forms import ImagesForm
from inventory.models import STCAdminImage

from .views import InventoryUserMixin


class DeleteSTCAdminImage(InventoryUserMixin, RedirectView):
    """Delete image from Product."""

    def get_redirect_url(self, image_id):
        """Return URL to redirect to."""
        stcadmin_image = get_object_or_404(
            STCAdminImage, pk=image_id)
        range_id = stcadmin_image.range_id
        stcadmin_image.delete()
        return reverse_lazy(
            'inventory:images', kwargs={'range_id': range_id})


class ImageFormView(InventoryUserMixin, FormView):
    """View for ImagesForm."""

    template_name = 'inventory/images.html'
    form_class = ImagesForm

    def dispatch(self, *args, **kwargs):
        """Process HTTP request."""
        self.range_id = self.kwargs.get('range_id')
        self.product_range = CCAPI.get_range(self.range_id)
        self.products = self.product_range.products
        for product in self.products:
            product.images = product.get_images()
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        """Get template context data."""
        context = super().get_context_data(*args, **kwargs)
        context['product_range'] = self.product_range
        context['products'] = self.products
        options = {
            o.option_name: {} for o in self.product_range.options if
            o.is_web_shop_select}
        for product in self.products:
            for o in [x for x in product.options if x.value]:
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
        """Return URL to redirect to after successful form submission."""
        return reverse_lazy(
            'inventory:images', kwargs={'range_id': self.range_id})

    def form_valid(self, form):
        """Process form request and return HttpResponse."""
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
