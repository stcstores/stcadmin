"""Views for handeling Product Images."""


from collections import defaultdict

from django.db.models import Max
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.edit import FormView

from inventory import models
from inventory.forms import ImagesForm

from .views import InventoryUserMixin


class ImageFormView(InventoryUserMixin, FormView):
    """View for ImagesForm."""

    template_name = "inventory/product_range/images.html"
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
        return models.ProductImageLink.objects.filter(product=product).aggregate(
            Max("position")
        )["position__max"]

    def get_success_url(self):
        """Return URL to redirect to after successful form submission."""
        return reverse_lazy(
            "inventory:images", kwargs={"range_pk": self.product_range.pk}
        )
