"""Views for handeling Product Images."""


import json
from collections import defaultdict

from django.db import transaction
from django.db.models import Max
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView
from django.views.generic.edit import FormView

from inventory import models
from inventory.forms import ImagesForm

from .views import InventoryUserMixin


class ImageFormView(InventoryUserMixin, FormView):
    """View for ImagesForm."""

    template_name = "inventory/product_range/images/image_page.html"
    form_class = ImagesForm

    def get_products(self):
        """Retrive product details from Cloud Commerce."""
        self.product_range = get_object_or_404(
            models.ProductRange, pk=self.kwargs.get("range_pk")
        )
        self.products = self.product_range.products.variations().prefetch_related(
            "images",
            "variation_option_values",
            "variation_option_values__variation_option",
        )

    def get_variation_options(self):
        """
        Return product ids and association vairation options.

        Returns:
            {variation_option: {option_value: [product_ids]}}
        """
        options = defaultdict(lambda: defaultdict(list))
        for product in self.products:
            variation = product.variation()
            for key, value in variation.items():
                options[key][value].append(product.pk)
        return {key: dict(value) for key, value in options.items()}

    def get_context_data(self, *args, **kwargs):
        """Get template context data."""
        context = super().get_context_data(*args, **kwargs)
        self.get_products()
        context["product_range"] = self.product_range
        context["product_range_images"] = self.product_range.images.order_by(
            "product_range_image_links"
        )
        context["products"] = {
            product: product.images.order_by("product_image_links")
            for product in self.products
        }
        context["options"] = self.get_variation_options()
        return context

    def form_valid(self, form):
        """Add submitted images."""
        self.product_range = get_object_or_404(
            models.ProductRange, pk=self.kwargs.get("range_pk")
        )
        if form.is_valid():
            products = form.cleaned_data["products"]
            images = list(self.request.FILES.getlist("images"))
            for image in images:
                db_image = models.ProductImage.objects.get_or_add_image(image)
                for i, product in enumerate(products, 1):
                    highest_position = self.get_highest_position(product)
                    models.ProductImageLink(
                        product=product, image=db_image, position=highest_position + i
                    ).save()
        return super().form_valid(form)

    def get_highest_position(self, product):
        """Return the position of the first new image."""
        highest_position = models.ProductImageLink.objects.filter(
            product=product
        ).aggregate(Max("position"))["position__max"]
        if highest_position is None:
            highest_position = -1
        return highest_position

    def get_success_url(self):
        """Return URL to redirect to after successful form submission."""
        return reverse_lazy(
            "inventory:images", kwargs={"range_pk": self.product_range.pk}
        )


@method_decorator(csrf_exempt, name="dispatch")
class SetImageOrderView(InventoryUserMixin, View):
    """Change order of images for a product."""

    @transaction.atomic
    def post(self, *args, **kwargs):
        """Process HTTP request."""
        data = json.loads(self.request.body)
        image_links = models.ProductImageLink.objects.filter(
            product__pk=data["product_pk"]
        ).select_related("image")
        image_order = [int(_) for _ in data["image_order"]]
        if not set(image_links.values_list("image__pk", flat=True)) == set(image_order):
            raise Exception("Did not get expected image IDs.")
        for link in image_links:
            link.position = image_order.index(link.image.pk)
            link.save()
        return JsonResponse(image_order, safe=False)


@method_decorator(csrf_exempt, name="dispatch")
class DeleteImage(InventoryUserMixin, View):
    """Remove image from a product."""

    def post(self, *args, **kwargs):
        """Process HTTP request."""
        data = json.loads(self.request.body)
        image_id = str(data["image_id"])
        product_id = str(data["product_id"])
        image_link = get_object_or_404(
            models.ProductImageLink,
            image__pk=image_id,
            product__pk=product_id,
        )
        image_link.delete()
        return JsonResponse({"Deleted": {"image": image_id, "product": product_id}})


@method_decorator(csrf_exempt, name="dispatch")
class ProductImages(InventoryUserMixin, TemplateView):
    """Remove image from a product."""

    template_name = "inventory/product_range/images/image_row.html"

    def post(self, *args, **kwargs):
        """Respond to POST requests."""
        return super().get(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        """Return a row of images for a product."""
        context = super().get_context_data(*args, **kwargs)
        product_id = self.request.POST["product_id"]
        image_links = models.ProductImageLink.objects.filter(
            product__id=product_id
        ).prefetch_related("image")
        context["product_id"] = product_id
        context["images"] = [link.image for link in image_links]
        return context
