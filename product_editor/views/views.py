"""Views for creating new products."""

import itertools
import os

from django.shortcuts import redirect
from django.views.generic.edit import FormView, View

from inventory.views import InventoryUserMixin
from product_editor import forms
from stcadmin import settings

from .editor_manager import NewProductManager


class DeleteProductView(InventoryUserMixin, View):
    """Clear new product from session and redirect to Basic Info."""

    def dispatch(self, *args, **kwargs):
        """Process request."""
        self.manager = NewProductManager(args[0])
        self.manager.delete_product()
        return redirect(self.manager.basic_info.url)


class BaseNewProductView(InventoryUserMixin, FormView):
    """Base class for new product form views."""

    def dispatch(self, *args, **kwargs):
        """Process request."""
        self.manager = NewProductManager(args[0])
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        """Return context data for template."""
        context = super().get_context_data(*args, **kwargs)
        context['manager'] = self.manager
        return context


class BasicInfo(BaseNewProductView):
    """View for the Basic Info page of the new product form."""

    template_name = 'product_editor/basic_info.html'
    form_class = forms.BasicInfo

    def get_initial(self, *args, **kwargs):
        """Get initial data for form."""
        existing_data = self.manager.basic_info.data
        if existing_data is not None:
            initial = existing_data
        else:
            initial = super().get_initial(*args, **kwargs)
        return initial

    def form_valid(self, form):
        """Save form data and return redirect."""
        self.manager.basic_info.data = form.cleaned_data
        if 'goto' in self.request.POST and ':' in self.request.POST['goto']:
            return redirect(self.request.POST['goto'])
        if 'variations' in self.request.POST:
            self.manager.product_type = NewProductManager.VARIATION
            return redirect(self.manager.variation_options.url)
        else:
            self.manager.product_type = NewProductManager.SINGLE
            return redirect(self.manager.listing_options.url)


class VariationOptions(BaseNewProductView):
    """View for the Variation Options page of the new product form."""

    template_name = 'product_editor/variation_options.html'
    form_class = forms.VariationOptions

    def get_initial(self, *args, **kwargs):
        """Get initial data for form."""
        initial = self.manager.variation_options.data
        if initial is None:
            initial = super().get_initial(*args, **kwargs)
        return initial

    def form_valid(self, form):
        """Save form data and return redirect."""
        self.manager.variation_options.data = form.cleaned_data
        if 'goto' in self.request.POST and ':' in self.request.POST['goto']:
            return redirect(self.request.POST['goto'])
        if 'back' in self.request.POST:
            return redirect(self.manager.basic_info.url)
        else:
            return redirect(self.manager.unused_variations.url)


class ListingOptions(BaseNewProductView):
    """View for the Listing Options page of the new product form."""

    template_name = 'product_editor/listing_options.html'
    form_class = forms.ListingOptions

    def get_initial(self, *args, **kwargs):
        """Get initial data for form."""
        initial = self.manager.listing_options.data
        if initial is None:
            initial = super().get_initial(*args, **kwargs)
        return initial

    def form_valid(self, form):
        """Save form data and return redirect."""
        self.manager.listing_options.data = form.cleaned_data
        if 'goto' in self.request.POST and ':' in self.request.POST['goto']:
            return redirect(self.request.POST['goto'])
        if 'back' in self.request.POST:
            return redirect(self.manager.basic_info.url)
        else:
            return redirect(self.manager.finish.url)


class BaseVariationProductView(BaseNewProductView):
    """Base class for variation pages of the new product form."""

    def get_form_kwargs(self, *args, **kwargs):
        """Get kwargs for form."""
        kwargs = super().get_form_kwargs(*args, **kwargs)
        existing_data = self._get_existing_data()
        kwargs['form_kwargs'] = [{
            'existing_data': existing_data,
            'variation_options': v,
            } for v in self.get_variation_combinations()]
        return kwargs

    def get_variation_combinations(self):
        """Return all combinations of variation options."""
        return self.manager.variations

    def get_context_data(self, *args, **kwargs):
        """Return context data for template."""
        context = super().get_context_data(*args, **kwargs)
        context['formset'] = context.pop('form')
        error_fields = []
        for form in context['formset']:
            for field in form:
                if field.errors:
                    error_fields.append(field.name)
        context['error_fields'] = set(error_fields)
        context['variation_values'] = self.get_variation_values()
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

    def form_valid(self, form):
        """Save form data and return redirect."""
        self._save_form_data(form.cleaned_data)
        if 'goto' in self.request.POST and ':' in self.request.POST['goto']:
            return redirect(self.request.POST['goto'])
        if 'back' in self.request.POST:
            return redirect(self._get_back_url())
        else:
            return redirect(self._get_continue_url())

    def _get_existing_data(self):
        raise NotImplementedError()

    def _save_form_data(self, data):
        raise NotImplementedError()

    def _get_back_url(self):
        raise NotImplementedError()

    def _get_continue_url(self):
        raise NotImplementedError()


class UnusedVariations(BaseVariationProductView):
    """View for Unused variations page of the new product form."""

    template_name = 'product_editor/unused_variations.html'
    form_class = forms.UnusedVariationsFormSet

    def get_variation_combinations(self):
        """Create and return all combination of variation options."""
        variation_options = self.get_variation_options()
        return list(
            dict(zip(variation_options, x)) for x in
            itertools.product(*variation_options.values()))

    def get_variation_options(self):
        """Return variation options."""
        variation_options = self.manager.variation_options.data
        return {
            key: value for key, value in variation_options.items()
            if len(value) > 0}

    def get_initial(self, *args, **kwargs):
        """Get initial data for form."""
        return self.get_variation_combinations()

    def _get_back_url(self):
        return self.manager.variation_options.url

    def _get_continue_url(self):
        return self.manager.variation_info.url

    def _get_existing_data(self):
        return self.manager.unused_variations.data

    def _save_form_data(self, data):
        self.manager.unused_variations.data = data


class VariationInfo(BaseVariationProductView):
    """View for the Variation Info page of the new product form."""

    template_name = 'product_editor/variation_info.html'
    form_class = forms.VariationInfoSet

    def get_form_kwargs(self, *args, **kwargs):
        """Get kwargs for form."""
        kwargs = super().get_form_kwargs(*args, **kwargs)
        kwargs['department'] = self.manager.basic_info.data[
            'department']['department']
        return kwargs

    def get_initial(self, *args, **kwargs):
        """Get initial data for form."""
        initial = self.get_variation_combinations()
        for init in initial:
            init.update(self.manager.basic_info.data)
            init['location'] = init['department']['bays']
        return initial

    def _get_back_url(self):
        return self.manager.unused_variations.url

    def _get_continue_url(self):
        return self.manager.variation_listing_options.url

    def _get_existing_data(self):
        return self.manager.variation_info.data

    def _save_form_data(self, data):
        self.manager.variation_info.data = data


class VariationListingOptions(BaseVariationProductView):
    """View for the Variation Listing Options page of the new product form."""

    template_name = 'product_editor/variation_listing_options.html'
    form_class = forms.VariationListingOptionsSet

    def get_initial(self, *args, **kwargs):
        """Get initial data for form."""
        initial = self.get_variation_combinations()
        return initial

    def _get_back_url(self):
        return self.manager.variation_info.url

    def _get_continue_url(self):
        return self.manager.finish.url

    def _get_existing_data(self):
        return self.manager.variation_listing_options.data

    def _save_form_data(self, data):
        self.manager.variation_listing_options.data = data


class FinishProduct(BaseNewProductView):
    """
    View for final page of the new product form.

    Start product creation process and return redirect.
    """

    product_log_directory = os.path.join(
        settings.MEDIA_ROOT, 'logs', 'products')

    def dispatch(self, *args, **kwargs):
        """Process request."""
        self.manager = NewProductManager(args[0])
        dir = os.path.join(self.product_log_directory, str(args[0].user.id))
        if not os.path.exists(dir):
            os.mkdir(dir)
        path = os.path.join(
            dir, '{}.json'.format(self.manager.basic_info.data['title']))
        most_recent = os.path.join(dir, 'most_recent.json')
        with open(path, 'w') as f:
            self.manager.save_json(f)
        with open(most_recent, 'w') as f:
            self.manager.save_json(f)
        range_id = self.manager.create_product()
        return redirect('inventory:product_range', range_id)
