"""Views for handeling Product Images."""


import json
from collections import defaultdict

from django.db import transaction
from django.http import HttpResponseRedirect, JsonResponse
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
        self.products = (
            self.product_range.products.variations()
            .active()
            .prefetch_related(
                "images",
                "variation_option_values",
                "variation_option_values__variation_option",
            )
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
            uploaded_images = list(self.request.FILES.getlist("images"))
            models.ProductImageLink.objects.add_images(
                products=products, uploaded_images=uploaded_images
            )
        return super().form_valid(form)

    def get_success_url(self):
        """Return URL to redirect to after successful form submission."""
        return reverse_lazy(
            "inventory:images", kwargs={"range_pk": self.product_range.pk}
        )


@method_decorator(csrf_exempt, name="dispatch")
class SetImageOrder(InventoryUserMixin, View):
    """Base view for changing image ordering."""

    @transaction.atomic
    def post(self, *args, **kwargs):
        """Process HTTP request."""
        data = json.loads(self.request.body)
        product_pk = data["product_pk"]
        image_order = [int(_) for _ in data["image_order"]]
        self.image_link_model.objects.set_image_order(
            product_pk=product_pk, image_order=image_order
        )
        return JsonResponse(image_order, safe=False)


class SetProductImageOrder(SetImageOrder):
    """Change the image order for a product."""

    image_link_model = models.ProductImageLink


class SetRangeImageOrder(SetImageOrder):
    """Change the image order for a product range."""

    image_link_model = models.ProductRangeImageLink


@method_decorator(csrf_exempt, name="dispatch")
class DeleteImage(InventoryUserMixin, View):
    """Base view for removing images from products."""

    def post(self, *args, **kwargs):
        """Process HTTP request."""
        data = json.loads(self.request.body)
        image_id = str(data["image_id"])
        product_id = str(data["product_id"])
        self.delete_image(product_id=product_id, image_id=image_id)
        return JsonResponse({"Deleted": {"image": image_id, "product": product_id}})


class DeleteProductImage(DeleteImage):
    """Remove and image from a product."""

    def delete_image(self, product_id, image_id):
        """Remove and image from a product."""
        models.ProductImageLink.objects.get(
            product__id=product_id, image__id=image_id
        ).delete()


class DeleteProductRangeImage(DeleteImage):
    """Remove an image from a product range."""

    def delete_image(self, product_id, image_id):
        """Remove an image from a product range."""
        models.ProductRangeImageLink.objects.get(
            product_range__id=product_id, image__id=image_id
        ).delete()


@method_decorator(csrf_exempt, name="dispatch")
class ProductImages(InventoryUserMixin, TemplateView):
    """Manage images for a product."""

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


@method_decorator(csrf_exempt, name="dispatch")
class ProductRangeImages(InventoryUserMixin, TemplateView):
    """Manage images for a product range."""

    template_name = "inventory/product_range/images/image_row.html"

    def post(self, *args, **kwargs):
        """Respond to POST requests."""
        return super().get(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        """Return a row of images for a product."""
        context = super().get_context_data(*args, **kwargs)
        range_id = self.request.POST["product_range_id"]
        image_links = models.ProductRangeImageLink.objects.filter(
            product_range__id=range_id
        ).prefetch_related("image")
        context["product_id"] = range_id
        context["images"] = [link.image for link in image_links]
        return context


class AddRangeImage(View):
    """View for adding images to product ranges."""

    def post(self, *args, **kwargs):
        """Add images to a product range."""
        product_range = get_object_or_404(
            models.ProductRange, pk=self.kwargs["range_pk"]
        )
        images = list(self.request.FILES.getlist("range_images"))
        models.ProductRangeImageLink.objects.add_images(
            product_range=product_range, uploaded_images=images
        )
        return HttpResponseRedirect(
            reverse_lazy("inventory:images", kwargs={"range_pk": product_range.pk})
        )
