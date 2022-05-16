"""Views for handeling Product Images."""


from collections import defaultdict
from copy import deepcopy
from uuid import uuid4

from django.core.files.uploadedfile import UploadedFile
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
        context["products"] = self.products
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
            for product in products:
                first_ordering = self.get_first_ordering(product)
                for ordering, uploaded_image in enumerate(images, first_ordering):
                    image = UploadedFile(
                        file=deepcopy(uploaded_image.file), name=str(uuid4())
                    )
                    image.file.seek(0)
                    models.ProductImage(
                        image_file=image, product=product, ordering=ordering
                    ).save()
        return super().form_valid(form)

    def get_first_ordering(self, product):
        """Return the position of the first new image."""
        last_image = product.images.active().order_by("-ordering").first()
        if last_image is not None:
            return last_image.ordering + 1
        else:
            return 0

    def get_success_url(self):
        """Return URL to redirect to after successful form submission."""
        return reverse_lazy(
            "inventory:images", kwargs={"range_pk": self.product_range.pk}
        )
