"""View for Product Range page."""

import itertools

from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views.generic.base import RedirectView, TemplateView
from django.views.generic.edit import FormView

from inventory import forms, models
from inventory.cloud_commerce_updater import PartialRangeUpdater

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

    template_name = "inventory/product_editor/edit_product.html"

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
        option_values = [
            [value.value for value in option]
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


class EditVariations(InventoryUserMixin, TemplateView):
    """View for editing the variation options of a range."""

    template_name = "inventory/product_editor/edit_variations.html"

    def get_context_data(self, *args, **kwargs):
        """Return the context for the template."""
        edit = get_object_or_404(models.ProductEdit.objects, pk=self.kwargs["edit_ID"])
        context = super().get_context_data(*args, **kwargs)
        context["edit"] = edit
        context["product_range"] = edit.partial_product_range
        context["product_options"] = edit.variation_options()
        context["used_values"] = edit.used_options()
        return context


class EditRangeDetails(DescriptionsView):
    """View for DescriptionForm."""

    template_name = "inventory/product_editor/edit_range_details.html"

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
    template_name = "inventory/product_editor/add_dropdown.html"

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
            "inventory:add_dropdown_values", kwargs={"edit_ID": self.edit.pk}
        )


class AddDropdownValues(InventoryUserMixin, TemplateView):
    """Add values to for a new dropdown."""

    template_name = "inventory/product_editor/add_dropdown_values.html"

    def dispatch(self, *args, **kwargs):
        """Load the formset."""
        self.edit = get_object_or_404(models.ProductEdit, pk=self.kwargs["edit_ID"])
        self.product_range = self.edit.partial_product_range
        self.formset = forms.NewDropDownValuesFormset(
            self.request.POST or None, form_kwargs=self.get_initial()
        )
        return super().dispatch(*args, **kwargs)

    def get_initial(self):
        """Return the initial values for the formset."""
        return [
            {
                "edit": self.edit,
                "product_range": self.product_range,
                "product": p,
                "initial": self.get_initial_for_product(p),
            }
            for p in self.product_range.products()
        ]

    def get_initial_for_product(self, product):
        """Return the initial values for a product for the formset."""
        initial = {"product_ID": product.id}
        for option in self.product_range.variation_options():
            try:
                initial[
                    f"option_{option.name}"
                ] = models.PartialProductOptionValueLink.objects.get(
                    product=product, product_option_value__product_option=option
                ).product_option_value
            except models.PartialProductOptionValueLink.DoesNotExist:
                pass
        return initial

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
        context["product_range"] = self.product_range
        context["formset"] = self.formset
        return context


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
            "inventory:edit_variations", kwargs={"edit_ID": self.edit.pk}
        )


class RemoveProductOptionValue(InventoryUserMixin, RedirectView):
    """Remove an unused product option value from the edit's product option value list."""

    def get_redirect_url(self, *args, **kwargs):
        """Remove a product option value and redirect."""
        edit = get_object_or_404(models.ProductEdit, pk=self.kwargs["edit_ID"])
        option = get_object_or_404(
            models.ProductOptionValue, pk=self.kwargs["option_value_ID"]
        )
        if option in edit.used_options():
            raise Exception("option used")
        else:
            edit.product_option_values.remove(option)
        return reverse_lazy("inventory:edit_variations", kwargs={"edit_ID": edit.pk})
