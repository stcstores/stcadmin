"""View for Product Range page."""

import itertools

from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic.base import RedirectView, TemplateView
from django.views.generic.edit import FormView

from inventory import forms, models
from inventory.cloud_commerce_updater import (
    PartialProductUpdater,
    PartialRangeUpdater,
    SaveEdit,
)

from .descriptions import DescriptionsView
from .views import InventoryUserMixin


class Continue(InventoryUserMixin, TemplateView):
    """List of products being edited or created."""

    template_name = "inventory/product_editor/continue.html"

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
        return models.ProductEdit.create_product_edit(self.request.user, product_range)


class StartNewProduct(InventoryUserMixin, FormView):
    """Start creating a new product."""

    template_name = "inventory/product_editor/edit_range_details.html"
    form_class = forms.DescriptionForm

    def form_valid(self, form):
        """Create a new partial product."""
        data = form.cleaned_data
        partial_range = models.PartialProductRange(
            SKU=models.PartialProductRange.get_new_SKU()
        )
        partial_range.save()
        updater = PartialRangeUpdater(partial_range, self.request.user)
        updater.set_name(data["title"])
        updater.set_department(data["department"])
        if data["description"]:
            updater.set_description(data["description"])
        updater.set_amazon_search_terms(data["search_terms"])
        updater.set_amazon_bullet_points(data["amazon_bullets"])
        self.product = models.PartialProduct(
            SKU=models.PartialProduct.get_new_SKU(), product_range=partial_range
        )
        self.product.save()
        self.edit = models.ProductEdit(
            user=self.request.user,
            product_range=None,
            partial_product_range=partial_range,
        )
        self.edit.save()
        return super().form_valid(form)

    def get_success_url(self):
        """Return the URL to redirect to on a successful form submission."""
        return reverse_lazy(
            "inventory:setup_variations", kwargs={"edit_ID": self.edit.pk}
        )


class EditProduct(InventoryUserMixin, TemplateView):
    """Main view for in progress product edits."""

    template_name = "inventory/product_editor/edit_product.html"

    def dispatch(self, *args, **kwargs):
        """If the product range is missing product option values redirect."""
        self.edit = models.ProductEdit.objects.get(pk=self.kwargs["edit_ID"])
        self.product_range = self.edit.partial_product_range
        if self.product_range.has_missing_product_option_values():
            messages.add_message(
                self.request, messages.ERROR, "Variations are missing product options."
            )
            return redirect(
                reverse_lazy(
                    "inventory:set_product_option_values",
                    kwargs={"edit_ID": self.edit.pk},
                )
            )
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        """Return the context for the template."""
        context = super().get_context_data(*args, **kwargs)
        context["edit"] = self.edit
        context["product_range"] = self.product_range
        context["variations"] = self.get_variation_matrix(
            self.edit.partial_product_range
        )
        context["ready_to_save"] = self.product_range.valid_variations() and all(
            (p.is_complete() for p in self.product_range.products())
        )
        return context

    def get_variation_matrix(self, product_range):
        """Return a dict of all possible variations for the range."""
        variations = {}
        products = product_range.products()
        option_values = [
            [value for value in option]
            for option in self.edit.variation_options().values()
        ]
        for options in itertools.product(*option_values):
            for product in products:
                if tuple(product.variation().values()) == options:
                    variations[options] = product
                    break
            else:
                variations[options] = None
        return variations


class SetupVariations(InventoryUserMixin, FormView):
    """Setup product options for a new product."""

    template_name = "inventory/product_editor/setup_variations.html"
    form_class = forms.SetupVariationsForm

    def dispatch(self, *args, **kwargs):
        """Process HTTP request."""
        self.edit = get_object_or_404(models.ProductEdit, pk=self.kwargs.get("edit_ID"))
        self.product_range = self.edit.partial_product_range
        return super(FormView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(*args, **kwargs)
        context["edit"] = self.edit
        return context

    def form_valid(self, form):
        """Add product options to the product edit."""
        data = form.cleaned_data
        updater = PartialRangeUpdater(self.product_range, self.request.user)
        for product_option, product_option_values in data.items():
            if product_option_values:
                updater.add_variation_product_option(product_option)
                self.edit.product_option_values.add(*product_option_values)
        return super().form_valid(form)

    def get_success_url(self, *args, **kwargs):
        """Redirect on successful validation of the form."""
        return reverse_lazy(
            "inventory:create_initial_variation",
            kwargs={
                "edit_ID": self.edit.pk,
                "product_ID": self.edit.partial_product_range.products()[0].pk,
            },
        )


class EditVariations(InventoryUserMixin, TemplateView):
    """View for editing the variation options of a range."""

    template_name = "inventory/product_editor/edit_variations.html"

    def get_context_data(self, *args, **kwargs):
        """Return the context for the template."""
        edit = get_object_or_404(models.ProductEdit.objects, pk=self.kwargs["edit_ID"])
        context = super().get_context_data(*args, **kwargs)
        context["edit"] = edit
        context["product_range"] = edit.partial_product_range
        context["variation_options"] = edit.partial_product_range.variation_options()
        context["listing_options"] = edit.partial_product_range.listing_options()
        context["values"] = edit.product_option_values.all()
        context[
            "pre_existing_options"
        ] = edit.partial_product_range.pre_existing_options()
        context["used_values"] = edit.partial_product_range.product_option_values()
        return context


class EditRangeDetails(DescriptionsView):
    """View for DescriptionForm."""

    template_name = "inventory/product_editor/edit_range_details.html"

    def dispatch(self, *args, **kwargs):
        """Process HTTP request."""
        self.edit = get_object_or_404(models.ProductEdit, pk=self.kwargs.get("edit_ID"))
        self.product_range = self.edit.partial_product_range
        return super(FormView, self).dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        """Return the context for the template."""
        context = super().get_context_data(*args, **kwargs)
        context["edit"] = self.edit
        context["product_range"] = self.edit.partial_product_range
        return context

    def form_valid(self, form):
        """Process form request and return HttpResponse."""
        updater = PartialRangeUpdater(self.product_range, self.request.user)
        updater.set_name(form.cleaned_data["title"])
        updater.set_description(form.cleaned_data["description"])
        updater.set_department(form.cleaned_data["department"])
        updater.set_amazon_search_terms(form.cleaned_data["search_terms"])
        updater.set_amazon_bullet_points(form.cleaned_data["amazon_bullets"])
        return super(FormView, self).form_valid(form)

    def get_success_url(self):
        """Return URL to redirect to after successful form submission."""
        return reverse_lazy("inventory:edit_product", kwargs={"edit_ID": self.edit.pk})


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
            for p in self.product_range.products()
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
            _ for _ in edit.partial_product_range.products() if _.pre_existing is False
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


class EditVariation(InventoryUserMixin, FormView):
    """Edit individual variations in the product editor."""

    template_name = "inventory/product_editor/edit_variation.html"
    form_class = forms.ProductForm

    def get_form_kwargs(self, *args, **kwargs):
        """Return kwargs for form."""
        self.edit = get_object_or_404(models.ProductEdit, pk=self.kwargs["edit_ID"])
        kwargs = super().get_form_kwargs()
        self.product = get_object_or_404(
            models.PartialProduct, pk=self.kwargs["product_ID"]
        )
        kwargs["product"] = self.product
        kwargs["user"] = self.request.user
        return kwargs

    def get_context_data(self, *args, **kwargs):
        """Get template context data."""
        context = super().get_context_data(*args, **kwargs)
        context["edit"] = self.edit
        context["product"] = self.product
        context["product_range"] = self.product.product_range
        return context

    def form_valid(self, form):
        """Process form request and return HttpResponse."""
        form.save(updater_class=PartialProductUpdater)
        messages.add_message(
            self.request, messages.SUCCESS, f"Product {self.product.SKU} Updated."
        )
        return super().form_valid(form)

    def get_success_url(self):
        """Return URL to redirect to after successful form submission."""
        return reverse_lazy(
            "inventory:edit_variation",
            kwargs={"edit_ID": self.edit.pk, "product_ID": self.product.id},
        )


class CreateInitialVariation(EditVariation):
    """Create the first product in a new range."""

    def get_success_url(self):
        """Return URL to redirect to after successful form submission."""
        product_options = self.edit.variation_options().values()
        for i, options in enumerate(itertools.product(*product_options)):
            if i == 1:
                for option in options:
                    models.PartialProductOptionValueLink.objects.get_or_create(
                        product=self.product, product_option_value=option
                    )
                continue
            self.edit.create_product(options)
        return reverse_lazy("inventory:edit_product", kwargs={"edit_ID": self.edit.pk})


class EditAllVariations(InventoryUserMixin, TemplateView):
    """View for editing partial product variations."""

    template_name = "inventory/product_editor/edit_all_variations.html"

    def dispatch(self, *args, **kwargs):
        """Load the formset."""
        self.edit = get_object_or_404(models.ProductEdit, pk=self.kwargs["edit_ID"])
        self.product_range = self.edit.partial_product_range
        self.formset = forms.VariationsFormSet(
            self.request.POST or None,
            form_kwargs=[{"product": p} for p in self.product_range.products()],
        )
        return super().dispatch(*args, **kwargs)

    def post(self, *args, **kwargs):
        """Process POST HTTP request."""
        if self.formset.is_valid():
            for form in self.formset:
                form.save(updater_class=PartialProductUpdater)
            return redirect(self.get_success_url())
        else:
            return super().get(*args, **kwargs)

    def get_success_url(self):
        """Return URL to redirect to after successful form submission."""
        return reverse_lazy("inventory:edit_product", kwargs={"edit_ID": self.edit.pk})

    def get_context_data(self, *args, **kwargs):
        """Get template context data."""
        context = super().get_context_data(*args, **kwargs)
        context["edit"] = self.edit
        context["product_range"] = self.product_range
        context["formset"] = self.formset
        context["variations"] = self.product_range.variation_values()
        return context


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


class DiscardChanges(InventoryUserMixin, RedirectView):
    """Discard changes in product editor."""

    def get_redirect_url(self, *args, **kwargs):
        """Delete the variation and redirect."""
        edit = get_object_or_404(models.ProductEdit, pk=self.kwargs["edit_ID"])
        edit.delete()
        if edit.product_range is not None:
            product_range_ID = edit.partial_product_range.range_ID
            return reverse_lazy(
                "inventory:product_range", kwargs={"range_id": product_range_ID}
            )
        else:
            return reverse_lazy("inventory:product_search")


class SaveChanges(InventoryUserMixin, RedirectView):
    """Save changes made in the product editor."""

    def get_redirect_url(self, *args, **kwargs):
        """Save changes and redirect."""
        edit = get_object_or_404(models.ProductEdit, pk=self.kwargs["edit_ID"])
        product_range_ID = edit.partial_product_range.range_ID
        SaveEdit(edit, self.request.user).save_edit_threaded()
        return reverse_lazy(
            "inventory:product_range", kwargs={"range_id": product_range_ID}
        )
