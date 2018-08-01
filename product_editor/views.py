"""Views for creating new products."""

import itertools
import os

from django.shortcuts import redirect
from django.views.generic.edit import FormView, View

from inventory.views import InventoryUserMixin
from product_editor import editor_manager, forms
from stcadmin import settings


class BaseProductView(InventoryUserMixin, editor_manager.ProductEditorBase, FormView):
    """Base class for new product form views."""

    def dispatch(self, *args, **kwargs):
        """Process request."""
        self.manager = self.get_manager(*args, **kwargs)
        self.page = self.get_page()
        return super().dispatch(*args, **kwargs)

    def get_page(self):
        """Return current page from manager."""
        return self.manager.get_page(self.name)

    def get_context_data(self, *args, **kwargs):
        """Return context data for template."""
        context = super().get_context_data(*args, **kwargs)
        context["manager"] = self.manager
        context["page"] = self.page
        return context

    def form_valid(self, form):
        """Save form data and return redirect."""
        self.page.data = form.cleaned_data
        return self.manager.get_redirect(self.page, self.request.POST)


class NewProductView:
    """Add New Product Manager to view."""

    manager_class = editor_manager.NewProductManager

    def get_manager(self, *args, **kwargs):
        """Return product manager."""
        return self.manager_class(args[0])


class EditProductView:
    """Add Edit Product Manager to view."""

    manager_class = editor_manager.EditProductManager

    def get_manager(self, *args, **kwargs):
        """Return product manager."""
        return self.manager_class(args[0], kwargs["range_id"])


class ClearProduct(InventoryUserMixin, View):
    """Clear product from session and redirect."""

    def dispatch(self, *args, **kwargs):
        """Process request."""
        self.manager = self.get_manager(*args, **kwargs)
        self.manager.clear_session()
        return self.manager.redirect_start()


class ClearNewProduct(ClearProduct, NewProductView):
    """Clear new product from session and redirect to Basic Info."""

    pass


class ClearEditedProduct(ClearProduct, EditProductView):
    """Clear product being edited from session and reload."""

    pass


class BasicInfo(BaseProductView):
    """View for the Basic Info page of the new product form."""

    template_name = "product_editor/basic_info.html"
    form_class = forms.BasicInfo
    name = editor_manager.ProductEditorBase.BASIC

    def get_initial(self, *args, **kwargs):
        """Get initial data for form."""
        existing_data = self.manager.basic_info.data
        if existing_data is not None:
            initial = existing_data
        else:
            initial = super().get_initial(*args, **kwargs)
        return initial


class NewBasicInfo(BasicInfo, NewProductView):
    """Basic Info view for new products."""

    pass


class EditBasicInfo(BasicInfo, EditProductView):
    """Basic Info view for existing products."""

    pass


class ProductInfo(BaseProductView):
    """View for the Single Product Info page of the product form."""

    template_name = "product_editor/product_info.html"
    form_class = forms.ProductInfo
    name = editor_manager.ProductEditorBase.PRODUCT_INFO

    def get_initial(self, *args, **kwargs):
        """Get initial data for form."""
        existing_data = self.manager.product_info.data
        if existing_data is not None:
            initial = existing_data
        else:
            initial = super().get_initial(*args, **kwargs)
            basic_info = self.manager.basic_info.data
            initial[self.LOCATION] = {
                self.WAREHOUSE: basic_info[self.DEPARTMENT],
                self.BAYS: [],
            }
        return initial

    def get_form_kwargs(self, *args, **kwargs):
        """Return key word arguments for form."""
        kwargs = super().get_form_kwargs(*args, **kwargs)
        return kwargs


class NewProductInfo(ProductInfo, NewProductView):
    """Product Info view for new products."""

    pass


class EditProductInfo(ProductInfo, EditProductView):
    """Product Info view for existing products."""

    pass


class VariationOptions(BaseProductView):
    """View for the Variation Options page of the new product form."""

    template_name = "product_editor/variation_options.html"
    form_class = forms.VariationOptions
    name = editor_manager.ProductEditorBase.VARIATION_OPTIONS

    def get_initial(self, *args, **kwargs):
        """Get initial data for form."""
        initial = self.manager.variation_options.data
        if initial is None:
            initial = super().get_initial(*args, **kwargs)
        return initial


class NewVariationOptions(VariationOptions, NewProductView):
    """Variation Options view for new products."""

    pass


class EditVariationOptions(VariationOptions, EditProductView):
    """Variation Options view for existing products."""

    pass


class ListingOptions(BaseProductView):
    """View for the Listing Options page of the new product form."""

    template_name = "product_editor/listing_options.html"
    form_class = forms.ListingOptions
    name = editor_manager.ProductEditorBase.LISTING_OPTIONS

    def get_initial(self, *args, **kwargs):
        """Get initial data for form."""
        initial = self.manager.listing_options.data
        if initial is None:
            initial = super().get_initial(*args, **kwargs)
        return initial


class NewListingOptions(ListingOptions, NewProductView):
    """Listing Options view for new products."""

    pass


class EditListingOptions(ListingOptions, EditProductView):
    """Listing Options view for existing products."""

    pass


class BaseVariationProductView(BaseProductView):
    """Base class for variation pages of the new product form."""

    def get_form_kwargs(self, *args, **kwargs):
        """Get kwargs for form."""
        kwargs = super().get_form_kwargs(*args, **kwargs)
        existing_data = self._get_existing_data()
        kwargs["form_kwargs"] = [
            {"existing_data": existing_data, "variation_options": v}
            for v in self.get_variation_combinations()
        ]
        return kwargs

    def get_variation_combinations(self):
        """Return all combinations of variation options."""
        return self.manager.variations

    def get_context_data(self, *args, **kwargs):
        """Return context data for template."""
        context = super().get_context_data(*args, **kwargs)
        context["formset"] = context.pop("form")
        error_fields = []
        for form in context["formset"]:
            for field in form:
                if field.errors:
                    error_fields.append(field.name)
        context["error_fields"] = set(error_fields)
        context["variation_values"] = self.get_variation_values()
        return context

    def get_variation_values(self):
        """Return dict of variation options and their values."""
        variation_combinations = self.get_variation_combinations()
        variation_values = {v: [] for v in variation_combinations[0]}
        for combination in variation_combinations:
            for key, value in combination.items():
                variation_values[key].append(value)
        for key, value in variation_values.items():
            variation_values[key] = sorted(list(set(value)))
        return variation_values

    def _get_existing_data(self):
        return self.page.data


class UnusedVariations(BaseVariationProductView):
    """View for Unused variations page of the new product form."""

    template_name = "product_editor/unused_variations.html"
    form_class = forms.UnusedVariationsFormSet
    name = editor_manager.ProductEditorBase.UNUSED_VARIATIONS

    def get_variation_combinations(self):
        """Create and return all combination of variation options."""
        variation_options = self.get_variation_options()
        return list(
            dict(zip(variation_options, x))
            for x in itertools.product(*variation_options.values())
        )

    def get_variation_options(self):
        """Return variation options."""
        variation_options = self.manager.variation_options.data
        return {
            key: value for key, value in variation_options.items() if len(value) > 0
        }

    def get_initial(self, *args, **kwargs):
        """Get initial data for form."""
        return self.get_variation_combinations()


class NewUnusedVariations(UnusedVariations, NewProductView):
    """Unused Variations view for new products."""

    pass


class EditUnusedVariations(UnusedVariations, EditProductView):
    """Unused Variations view for existing products."""

    pass


class VariationInfo(BaseVariationProductView):
    """View for the Variation Info page of the new product form."""

    template_name = "product_editor/variation_info.html"
    form_class = forms.VariationInfoSet
    name = editor_manager.ProductEditorBase.VARIATION_INFO

    def get_form_kwargs(self, *args, **kwargs):
        """Get kwargs for form."""
        kwargs = super().get_form_kwargs(*args, **kwargs)
        return kwargs

    def get_initial(self, *args, **kwargs):
        """Get initial data for form."""
        initial = self.get_variation_combinations()
        for init in initial:
            init.update(self.manager.product_info.data)
            init.pop(self.PRODUCT_ID)
        return initial


class NewVariationInfo(VariationInfo, NewProductView):
    """Variation Info view for new proudcts."""

    pass


class EditVariationInfo(VariationInfo, EditProductView):
    """Variation Info view for existing products."""

    def get_form(self, form_class=None):
        """Return an instance of the form to be used in this view."""
        formset = super().get_form(form_class)
        for form in formset:
            form.fields.pop(self.STOCK_LEVEL)
        return formset


class VariationListingOptions(BaseVariationProductView):
    """View for the Variation Listing Options page of the new product form."""

    template_name = "product_editor/variation_listing_options.html"
    form_class = forms.VariationListingOptionsSet
    name = editor_manager.ProductEditorBase.VARIATION_LISTING_OPTIONS

    def get_initial(self, *args, **kwargs):
        """Get initial data for form."""
        initial = self.get_variation_combinations()
        return initial


class NewVariationListingOptions(VariationListingOptions, NewProductView):
    """Variation Listing Options view for new products."""

    pass


class EditVariationListingOptions(VariationListingOptions, EditProductView):
    """Variation Listing Options view for exisiting products."""

    pass


class FinishProduct(BaseProductView):
    """Complete product creation or update."""

    product_log_directory = os.path.join(settings.MEDIA_ROOT, "logs", "products")

    def dispatch(self, *args, **kwargs):
        """Process request."""
        self.manager = self.get_manager(*args, **kwargs)
        dir = os.path.join(self.product_log_directory, str(args[0].user.id))
        if not os.path.exists(dir):
            os.mkdir(dir)
        path = os.path.join(
            dir, "{}.json".format(self.manager.basic_info.data[self.TITLE])
        )
        most_recent = os.path.join(dir, "most_recent.json")
        with open(path, "w") as f:
            self.manager.save_json(f)
        with open(most_recent, "w") as f:
            self.manager.save_json(f)
        range_id = self.manager.save_product()
        return redirect("inventory:product_range", range_id)


class FinishNewProduct(FinishProduct, NewProductView):
    """
    View for final page of the new product form.

    Start product creation process and return redirect.
    """

    pass


class FinishEditProduct(FinishProduct, EditProductView):
    """Apply changes to product."""

    pass
