"""View for Product Range page."""

import itertools
import json
from collections import defaultdict

from django.contrib import messages
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
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
            models.ProductRange, pk=self.kwargs.get("range_pk")
        )
        product_count = product_range.products.count()
        if product_count == 0:
            redirect_name = "inventory:create_initial_variation"

        elif product_count == 1:
            redirect_name = "inventory:setup_variations"
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
        context["options"] = json.dumps(
            {key: value.label for key, value in context["form"].fields.items()}
        )
        return context

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


class BaseProductRangeEditView(InventoryUserMixin, TemplateView):
    """Base view for product range edits."""

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
        option_values = self.product_range.variation_option_values().values()
        for options in itertools.product(*option_values):
            for product in products:
                if tuple(product.variation().values()) == options:
                    variations[options] = product
                    break
            else:
                variations[options] = None
        return variations


class EditNewProduct(BaseProductRangeEditView):
    """View for finalising new products."""

    template_name = "inventory/product_editor/edit_new_product.html"


class EditProduct(BaseProductRangeEditView):
    """Main view for in progress product edits."""

    template_name = "inventory/product_editor/edit_product.html"


class CompleteNewProduct(InventoryUserMixin, RedirectView):
    """Complete a new product."""

    def get_redirect_url(self, *args, **kwargs):
        """Complete new product and redirect."""
        product_range = get_object_or_404(
            models.ProductRange, pk=self.kwargs.get("range_pk")
        )
        product_range.complete_new_range(self.request.user)
        return product_range.get_absolute_url()


class AddProductOption(InventoryUserMixin, FormView):
    """Add a new product option to a partial product range."""

    form_class = forms.AddProductOption
    template_name = "inventory/product_editor/add_product_option.html"

    name = None
    variation = None

    def get_form_kwargs(self, *args, **kwargs):
        """Return the kwargs for insanciating the form."""
        kwargs = super().get_form_kwargs(*args, **kwargs)
        self.edit = get_object_or_404(models.ProductEdit, pk=self.kwargs.get("edit_ID"))
        kwargs["edit"] = self.edit
        kwargs["variation"] = self.variation
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, *args, **kwargs):
        """Return the context for the template."""
        context = super().get_context_data(*args, **kwargs)
        context["edit"] = self.edit
        context["product_range"] = self.edit.partial_product_range
        context["name"] = self.name
        return context

    def form_valid(self, form):
        """Add the new variation product option and values to the product range."""
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        """Return the URL to redirect to on a successful form submission."""
        return reverse_lazy("inventory:edit_product", kwargs={"edit_ID": self.edit.pk})


class AddDropdown(AddProductOption):
    """Add a variation product option to a partial product range."""

    name = "Dropdown"
    variation = True


class AddListingOption(AddProductOption):
    """Add a listing product option to a partial product range."""

    name = "Listing Option"
    variation = False


class SetProductOptionValues(InventoryUserMixin, TemplateView):
    """Add values to for a new dropdown."""

    template_name = "inventory/product_editor/set_product_option_values.html"

    def dispatch(self, *args, **kwargs):
        """Load the formset."""
        self.edit = get_object_or_404(models.ProductEdit, pk=self.kwargs["edit_ID"])
        self.product_range = self.edit.partial_product_range
        self.formset = forms.SetProductOptionValuesFormset(
            self.request.POST or None, form_kwargs=self.get_initial()
        )
        return super().dispatch(*args, **kwargs)

    def get_initial(self):
        """Return the initial values for the formset."""
        return [
            {"edit": self.edit, "product_range": self.product_range, "product": p}
            for p in self.product_range.products.variations()
        ]

    def post(self, *args, **kwargs):
        """Process POST HTTP request."""
        if self.formset.is_valid():
            self.formset.save()
            return redirect(self.get_success_url())
        else:
            return super().get(*args, **kwargs)

    def get_success_url(self):
        """Return URL to redirect to after successful form submission."""
        return reverse_lazy("inventory:edit_product", kwargs={"edit_ID": self.edit.id})

    def get_context_data(self, *args, **kwargs):
        """Get template context data."""
        context = super().get_context_data(*args, **kwargs)
        context["edit"] = self.edit
        context["product_range"] = self.product_range
        context["formset"] = self.formset
        return context


class RemoveDropdown(InventoryUserMixin, RedirectView):
    """Remove a new dropdown from a parital product range."""

    def get_redirect_url(self, *args, **kwargs):
        """Remove a product option and redirect."""
        edit = get_object_or_404(models.ProductEdit, pk=self.kwargs["edit_ID"])
        option = get_object_or_404(
            models.ProductOption, pk=self.kwargs["product_option_ID"]
        )
        option_link = get_object_or_404(
            models.PartialProductRangeSelectedOption,
            product_range=edit.partial_product_range,
            product_option=option,
            pre_existing=False,
        )
        products = [
            _
            for _ in edit.partial_product_range.products.variations()
            if _.pre_existing is False
        ]
        for product in products:
            product.delete()
        option_link.delete()
        edit.product_option_values.set(
            edit.product_option_values.exclude(product_option=option)
        )
        models.PartialProductOptionValueLink.objects.filter(
            product__product_range=edit.partial_product_range,
            product_option_value__product_option=option,
        ).delete()
        return reverse_lazy("inventory:edit_variations", kwargs={"edit_ID": edit.pk})


class AddProductOptionValues(InventoryUserMixin, FormView):
    """Add product option values to a product edit."""

    form_class = forms.AddProductOptionValuesForm
    template_name = "inventory/product_editor/add_product_option_values.html"

    def dispatch(self, *args, **kwargs):
        """Get model objects."""
        self.edit = get_object_or_404(
            models.ProductEdit.objects, pk=self.kwargs["edit_ID"]
        )
        self.product_option = get_object_or_404(
            models.ProductOption.objects, pk=self.kwargs["product_option_ID"]
        )
        return super().dispatch(*args, **kwargs)

    def get_form_kwargs(self, *args, **kwargs):
        """Return the kwargs for the form."""
        form_kwargs = super().get_form_kwargs(*args, **kwargs)
        form_kwargs["edit"] = self.edit
        form_kwargs["product_option"] = self.product_option
        return form_kwargs

    def get_context_data(self, *args, **kwargs):
        """Return the context for the template."""
        context = super().get_context_data(*args, **kwargs)
        context["edit"] = self.edit
        context["product_range"] = self.edit.partial_product_range
        context["product_option"] = self.product_option
        return context

    def form_valid(self, form):
        """Add the new variation product option and values to the product range."""
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        """Return the URL to redirect to on a successful form submission."""
        return reverse_lazy(
            "inventory:set_product_option_values", kwargs={"edit_ID": self.edit.pk}
        )


class RemoveProductOptionValue(InventoryUserMixin, RedirectView):
    """Remove an unused product option value from the edit's product option value list."""

    def get_redirect_url(self, *args, **kwargs):
        """Remove a product option value and redirect."""
        edit = get_object_or_404(models.ProductEdit, pk=self.kwargs["edit_ID"])
        option = get_object_or_404(
            models.ProductOptionValue, pk=self.kwargs["option_value_ID"]
        )
        if option in edit.partial_product_range.product_option_values():
            raise Exception("option used")
        else:
            edit.product_option_values.remove(option)
        return reverse_lazy("inventory:edit_variations", kwargs={"edit_ID": edit.pk})


class EditVariation(InventoryUserMixin, UpdateView):
    """Edit individual variations in the product editor."""

    template_name = "inventory/product_editor/edit_variation.html"
    model = models.Product
    form_class = forms.EditProductForm

    def form_valid(self, form):
        """Process form request and return HttpResponse."""
        form.save()
        self.product = form.instance
        messages.add_message(
            self.request, messages.SUCCESS, f"{self.product.full_name} Updated"
        )
        return super().form_valid(form)

    def get_success_url(self):
        """Return URL to redirect to after successful form submission."""
        return reverse_lazy(
            "inventory:edit_new_product",
            kwargs={"range_pk": self.product.product_range.pk},
        )

    def get_context_data(self, *args, **kwargs):
        """Get template context data."""
        context_data = super().get_context_data(*args, **kwargs)
        form = context_data["form"]
        context_data["product"] = form.instance
        context_data["product_range"] = form.instance.product_range
        return context_data


class CreateVariation(InventoryUserMixin, RedirectView):
    """View for creating new variations."""

    def get_redirect_url(self, *args, **kwargs):
        """Create new variation and redirect."""
        edit = get_object_or_404(models.ProductEdit, pk=self.kwargs["edit_ID"])
        options = self.get_product_options()
        edit.create_product(options)
        return reverse_lazy("inventory:edit_product", kwargs={"edit_ID": edit.pk})

    def get_product_options(self):
        """Return a list of the new products variation product options."""
        options = [
            get_object_or_404(models.ProductOptionValue, id=option_id)
            for key, option_id in self.request.POST.items()
            if key.isdigit()
        ]
        return options


class DeleteVariation(InventoryUserMixin, RedirectView):
    """Delete a partial product."""

    def get_redirect_url(self, *args, **kwargs):
        """Delete the variation and redirect."""
        edit = get_object_or_404(models.ProductEdit, pk=self.kwargs["edit_ID"])
        product = get_object_or_404(models.PartialProduct, pk=self.kwargs["product_ID"])
        if not product.pre_existing:
            product.delete()
        return reverse_lazy("inventory:edit_product", kwargs={"edit_ID": edit.pk})


class DiscardNewRange(InventoryUserMixin, RedirectView):
    """Discard changes in product editor."""

    def get_redirect_url(self, *args, **kwargs):
        """Delete the variation and redirect."""
        product_range = get_object_or_404(
            models.ProductRange, pk=self.kwargs["range_pk"]
        )
        product_range.products.all().delete()
        product_range.delete()
        return reverse_lazy("inventory:product_search")
