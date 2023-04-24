"""View for Product Range page."""

import itertools
import json
from collections import defaultdict

from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic.base import RedirectView, TemplateView
from django.views.generic.edit import CreateView, FormView, UpdateView

from inventory import forms, models

from .views import InventoryUserMixin


class Continue(InventoryUserMixin, TemplateView):
    """List of products being edited or created."""

    template_name = "inventory/product_editor/continue.html"

    def get_context_data(self, *args, **kwargs):
        """Return the context for the template."""
        context = super().get_context_data(*args, **kwargs)
        context["user_product_ranges"] = models.ProductRange.creating.filter(
            managed_by=self.request.user
        )
        others_ranges = models.ProductRange.creating.exclude(
            managed_by=self.request.user
        )
        others_product_ranges = defaultdict(list)
        for product_range in others_ranges:
            others_product_ranges[product_range.managed_by].append(product_range)
        context["others_product_ranges"] = dict(others_product_ranges)
        return context


class ResumeEditingProduct(InventoryUserMixin, RedirectView):
    """View for redirecting to the correct page to continue creating a product."""

    def get_redirect_url(self, *args, **kwargs):
        """Return the URL to redirect to."""
        product_range = get_object_or_404(
            models.ProductRange,
            pk=self.kwargs.get("range_pk"),
            status=models.ProductRange.CREATING,
        )
        product_count = product_range.products.count()
        if product_count == 0:
            redirect_name = "inventory:create_initial_variation"

        elif product_count == 1:
            product = product_range.products.first()
            if isinstance(product, models.InitialVariation):
                redirect_name = "inventory:setup_variations"
            else:
                redirect_name = "inventory:edit_new_product"
        else:
            redirect_name = "inventory:edit_all_variations"
        return reverse_lazy(redirect_name, kwargs={"range_pk": product_range.pk})


class StartNewProduct(InventoryUserMixin, CreateView):
    """Start creating a new product."""

    template_name = "inventory/product_editor/range_form.html"
    form_class = forms.CreateRangeForm

    def get_initial(self, *args, **kwargs):
        """Return initial values for the form."""
        initial = super().get_initial()
        initial.update({"managed_by": self.request.user, "sku": models.new_range_sku()})
        return initial

    def get_success_url(self):
        """Return the URL to redirect to on a successful form submission."""
        return reverse(
            "inventory:create_initial_variation", kwargs={"range_pk": self.object.pk}
        )


class EditRangeDetails(InventoryUserMixin, UpdateView):
    """View for CreateRangeForm."""

    form_class = forms.EditRangeForm
    model = models.ProductRange
    template_name = "inventory/product_editor/range_form.html"

    def get_success_url(self):
        """Return URL to redirect to after successful form submission."""
        return reverse(
            "inventory:edit_new_product", kwargs={"range_pk": self.object.pk}
        )


class CreateInitialVariation(CreateView):
    """Create the first product in a new range."""

    form_class = forms.InitialVariationForm
    template_name = "inventory/product_editor/create_initial_variation.html"

    def get_initial(self, *args, **kwargs):
        """Return initial form values."""
        initial = super().get_initial(*args, **kwargs)
        self.product_range = get_object_or_404(
            models.ProductRange, pk=self.kwargs.get("range_pk")
        )
        initial.update({"product_range": self.product_range})
        return initial

    def get_success_url(self):
        """Return URL to redirect to after successful form submission."""
        range_pk = self.object.product_range.pk
        if self.object.polymorphic_ctype.model_class() == models.Product:
            return reverse_lazy(
                "inventory:edit_new_product", kwargs={"range_pk": range_pk}
            )
        else:
            return reverse_lazy(
                "inventory:setup_variations", kwargs={"range_pk": range_pk}
            )


class SetupVariations(InventoryUserMixin, FormView):
    """Setup product options for a new product."""

    template_name = "inventory/product_editor/setup_variations.html"
    form_class = forms.SetupVariationsForm

    def dispatch(self, *args, **kwargs):
        """Process HTTP request."""
        self.product_range = get_object_or_404(
            models.ProductRange, pk=self.kwargs.get("range_pk")
        )
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(*args, **kwargs)
        context["product_range"] = self.product_range
        context["options"] = self.get_options(context["form"])
        return context

    def get_options(self, form):
        """Return a dict of product options."""
        return json.dumps({key: value.label for key, value in form.fields.items()})

    def form_valid(self, form):
        """Create variation products."""
        initial_variation = models.InitialVariation.objects.get(
            product_range=self.product_range
        )
        variations = [
            _["options"]
            for _ in json.loads(form.cleaned_data["variations"])
            if _["included"] is True
        ]
        with transaction.atomic():
            initial_variation.create_variations(variations)
            initial_variation.delete()
        return super().form_valid(form)

    def get_success_url(self, *args, **kwargs):
        """Redirect on successful validation of the form."""
        return reverse_lazy(
            "inventory:edit_all_variations",
            kwargs={"range_pk": self.product_range.pk},
        )


class EditAllVariations(InventoryUserMixin, FormView):
    """View for editing partial product variations."""

    template_name = "inventory/product_editor/edit_all_variations.html"
    form_class = forms.ProductFormset

    def get_form_kwargs(self, *args, **kwargs):
        """Load the formset."""
        self.product_range = get_object_or_404(
            models.ProductRange, pk=self.kwargs["range_pk"]
        )
        kwargs = super().get_form_kwargs(*args, **kwargs)
        kwargs.update(
            {
                "form_kwargs": [
                    {"instance": product}
                    for product in self.product_range.products.all()
                ]
            }
        )
        return kwargs

    def get_context_data(self, *args, **kwargs):
        """Get template context data."""
        context = super().get_context_data(*args, **kwargs)
        context["product_range"] = self.product_range
        context["formset"] = context["form"]
        context["variations"] = self.product_range.variation_option_values()
        return context

    def form_valid(self, formset):
        """Process POST HTTP request."""
        for form in formset:
            form.save()
        return super().form_valid(formset)

    def get_success_url(self):
        """Return URL to redirect to after successful form submission."""
        return reverse_lazy(
            "inventory:edit_new_product", kwargs={"range_pk": self.product_range.pk}
        )


class EditNewProduct(InventoryUserMixin, TemplateView):
    """Base view for product range edits."""

    template_name = "inventory/product_editor/edit_new_product.html"

    def get_context_data(self, *args, **kwargs):
        """Get template context data."""
        self.product_range = get_object_or_404(
            models.ProductRange, pk=self.kwargs.get("range_pk")
        )
        context = super().get_context_data(*args, **kwargs)
        context["product_range"] = self.product_range
        context["variations"] = self.get_variation_matrix(self.product_range)
        return context

    def get_variation_matrix(self, product_range):
        """Return a dict of all possible variations for the range."""
        variations = {}
        products = product_range.products.all()
        option_values = product_range.variation_option_values().values()
        for options in itertools.product(*option_values):
            for product in products:
                if tuple(product.variation().values()) == options:
                    variations[options] = product
                    break
            else:
                variations[options] = None
        return variations


class CompleteNewProduct(InventoryUserMixin, RedirectView):
    """Complete a new product."""

    def get_redirect_url(self, *args, **kwargs):
        """Complete new product and redirect."""
        product_range = get_object_or_404(
            models.ProductRange, pk=self.kwargs.get("range_pk")
        )
        product_range.complete_new_range(self.request.user)
        return product_range.get_absolute_url()


class EditNewVariation(InventoryUserMixin, UpdateView):
    """Edit individual variations in the product editor."""

    template_name = "inventory/product_editor/edit_new_variation.html"
    model = models.Product
    form_class = forms.EditProductForm

    def get_context_data(self, *args, **kwargs):
        """Get template context data."""
        context_data = super().get_context_data(*args, **kwargs)
        form = context_data["form"]
        context_data["product"] = form.instance
        context_data["product_range"] = form.instance.product_range
        return context_data

    def get_success_url(self):
        """Return URL to redirect to after successful form submission."""
        messages.add_message(
            self.request, messages.SUCCESS, f"{self.object.full_name} Updated"
        )
        return reverse_lazy(
            "inventory:edit_new_product",
            kwargs={"range_pk": self.object.product_range.pk},
        )


class DiscardNewRange(InventoryUserMixin, RedirectView):
    """Discard changes in product editor."""

    def get_redirect_url(self, *args, **kwargs):
        """Delete the variation and redirect."""
        product_range = get_object_or_404(
            models.ProductRange, pk=self.kwargs["range_pk"]
        )
        if product_range.status != models.ProductRange.CREATING:
            raise ValueError("Cannot delete completed product range.")
        product_range.products.all().delete()
        product_range.delete()
        return reverse_lazy("inventory:product_search")
