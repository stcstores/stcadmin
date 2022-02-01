"""Views for handeling Product Images."""

import json
from collections import defaultdict

from ccapi import CCAPI
from django.urls import reverse_lazy
from django.views.generic.edit import FormView

from inventory.forms import ImagesForm

from .views import InventoryUserMixin


class ImageFormView(InventoryUserMixin, FormView):
    """View for ImagesForm."""

    template_name = "inventory/images.html"
    form_class = ImagesForm

    def get_products(self):
        """Retrive product details from Cloud Commerce."""
        self.range_id = self.kwargs.get("range_id")
        self.product_range = CCAPI.get_range(self.range_id)
        self.products = self.product_range.products
        for product in self.products:
            product.images = product.get_images()

    def get_options(self):
        """Return a dict of applicable product options."""
        options = {
            o.option_name: defaultdict(list)
            for o in self.product_range.options
            if o.is_web_shop_select
        }
        for product in self.products:
            for o in [x for x in product.options if x.value]:
                if o.option_name in options:
                    value = o.value.value
                    if value in options[o.option_name]:
                        options[o.option_name][value].append(product.id)
                    else:
                        options[o.option_name][value] = [product.id]
        for key, value in options.items():
            options[key] = dict(value)
        return options

    def get_context_data(self, *args, **kwargs):
        """Get template context data."""
        self.get_products()
        context = super().get_context_data(*args, **kwargs)
        context["product_range"] = self.product_range
        context["products"] = self.products
        context["options"] = self.get_options()
        return context

    def get_success_url(self):
        """Return URL to redirect to after successful form submission."""
        return reverse_lazy("inventory:images", kwargs={"range_id": self.range_id})

    def form_valid(self, form):
        """Process form request and return HttpResponse."""
        self.get_products()
        product_ids = json.loads(form.cleaned_data["product_ids"])
        cc_files = self.request.FILES.getlist("cloud_commerce_images")
        for image in cc_files:
            image_file = image
            CCAPI.upload_image(product_ids=product_ids, image_file=image_file)
        return super().form_valid(form)
