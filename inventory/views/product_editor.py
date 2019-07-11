"""View for Product Range page."""

import itertools

from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.views.generic.base import RedirectView, TemplateView
from django.views.generic.edit import FormView

from inventory import forms, models
from inventory.cloud_commerce_updater import PartialRangeUpdater

from .descriptions import DescriptionsView
from .views import InventoryUserMixin


class Continue(InventoryUserMixin, TemplateView):
    """List of products being edited or created."""

    template_name = "inventory/continue.html"

    def get_context_data(self, *args, **kwargs):
        """Return the context for the template."""
        context = super().get_context_data(*args, **kwargs)
        context["user_edits"] = models.ProductEdit.objects.filter(
            user=self.request.user
        )
        context["others_edits"] = models.ProductEdit.objects.exclude(
            user=self.request.user
        )
        return context


class StartEditingProduct(InventoryUserMixin, RedirectView):
    """Create a new product edit if one does not exist and redirect."""

    permanent = False
    query_string = True

    def get_redirect_url(self, *args, **kwargs):
        """Create a new product edit if one does not exist and redirect."""
        product_range = models.ProductRange.objects.get(range_ID=kwargs["range_ID"])
        try:
            edit = models.ProductEdit.objects.get(product_range=product_range)
        except models.ProductEdit.DoesNotExist:
            edit = self.start_edit(product_range)
        return reverse_lazy("inventory:edit_product", kwargs={"edit_ID": edit.pk})

    def start_edit(self, product_range):
        """Create a new product edit."""
        partial_product_range = models.PartialProductRange.copy_range(product_range)
        edit = models.ProductEdit(
            product_range=product_range,
            partial_product_range=partial_product_range,
            user=self.request.user,
        )
        edit.save()
        option_values = [
            _.product_option_value
            for _ in models.ProductOptionValueLink.objects.filter(
                product__product_range=product_range
            )
        ]
        for value in option_values:
            edit.product_option_values.add(value)
        return edit


class EditProduct(InventoryUserMixin, TemplateView):
    """Main view for in progress product edits."""

    template_name = "inventory/edit_product.html"

    def get_context_data(self, *args, **kwargs):
        """Return the context for the template."""
        context = super().get_context_data(*args, **kwargs)
        self.edit = models.ProductEdit.objects.get(pk=self.kwargs["edit_ID"])
        context["edit"] = self.edit
        context["product_range"] = self.edit.partial_product_range
        context["variations"] = self.get_variation_matrix(
            self.edit.partial_product_range
        )
        return context

    def get_variation_matrix(self, product_range):
        """Return a dict of all possible variations for the range."""
        variations = {}
        products = product_range.products()
        for options in itertools.product(*self.edit.variation_options().values()):
            for product in products:
                if tuple(product.variation().values()) == options:
                    variations[options] = product
                    break
            else:
                variations[options] = None
        return variations


class EditVariations(InventoryUserMixin, TemplateView):
    """View for editing the variation options of a range."""

    template_name = "inventory/edit_variations.html"

    def get_context_data(self, *args, **kwargs):
        """Return the context for the template."""
        edit = get_object_or_404(models.ProductEdit.objects, pk=self.kwargs["edit_ID"])
        context = super().get_context_data(*args, **kwargs)
        context["edit"] = edit
        context["product_range"] = edit.partial_product_range
        context["product_options"] = edit.variation_options
        return context


class EditRangeDetails(DescriptionsView):
    """View for DescriptionForm."""

    template_name = "inventory/edit_range_details.html"

    def dispatch(self, *args, **kwargs):
        """Process HTTP request."""
        self.edit = get_object_or_404(models.ProductEdit, pk=self.kwargs.get("edit_ID"))
        self.product_range = self.edit.partial_product_range
        return super(FormView, self).dispatch(*args, **kwargs)

    def form_valid(self, form):
        """Process form request and return HttpResponse."""
        updater = PartialRangeUpdater(self.product_range)
        updater.set_name(form.cleaned_data["title"])
        updater.set_description(form.cleaned_data["description"])
        updater.set_amazon_bullet_points("|".join(form.cleaned_data["amazon_bullets"]))
        updater.set_amazon_search_terms("|".join(form.cleaned_data["search_terms"]))
        return super(FormView, self).form_valid(form)

    def get_success_url(self):
        """Return URL to redirect to after successful form submission."""
        return reverse_lazy("inventory:edit_product", kwargs={"edit_ID": self.edit.pk})


class AddDropdown(InventoryUserMixin, FormView):
    """Add a new variation product option to a partial product range."""

    form_class = forms.AddVariationOption
    template_name = "inventory/add_dropdown.html"

    def get_form_kwargs(self, *args, **kwargs):
        """Return the kwargs for insanciating the form."""
        kwargs = super().get_form_kwargs(*args, **kwargs)
        self.edit = get_object_or_404(models.ProductEdit, pk=self.kwargs.get("edit_ID"))
        kwargs["edit"] = self.edit
        return kwargs

    def get_context_data(self, *args, **kwargs):
        """Return the context for the template."""
        context = super().get_context_data(*args, **kwargs)
        context["edit"] = self.edit
        return context

    def form_valid(self, form):
        """Add the new variation product option and values to the product range."""
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        """Return the URL to redirect to on a successful form submission."""
        return reverse_lazy(
            "inventory:edit_variations", kwargs={"edit_ID": self.edit.pk}
        )
