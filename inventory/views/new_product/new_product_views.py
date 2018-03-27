"""Views for creating new products."""

import itertools

from django.shortcuts import redirect
from django.views.generic.edit import FormView, View

from inventory import forms

from ..views import InventoryUserMixin
from .new_product_manager import NewProductManager


class DeleteProductView(InventoryUserMixin, View):
    """Clear new product from session and redirect to Basic Info."""

    def dispatch(self, *args, **kwargs):
        self.manager = NewProductManager(args[0])
        self.manager.delete_product()
        return redirect('inventory:new_product_basic_info')


class BaseNewProductView(InventoryUserMixin, FormView):
    """Base class for new product form views."""

    def dispatch(self, *args, **kwargs):
        self.manager = NewProductManager(args[0])
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['manager'] = self.manager
        return context


class BasicInfo(BaseNewProductView):
    """View for the Basic Info page of the new product form."""

    template_name = 'inventory/new_product/basic_info.html'
    form_class = forms.NewProductBasicForm

    def get_initial(self, *args, **kwargs):
        existing_data = self.manager.basic_info.data
        if existing_data is not None:
            initial = existing_data
        else:
            initial = super().get_initial(*args, **kwargs)
        return initial

    def form_valid(self, form):
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

    template_name = 'inventory/new_product/variation_options.html'
    form_class = forms.VariationOptionsForm

    def get_initial(self, *args, **kwargs):
        initial = self.manager.variation_options.data
        if initial is None:
            initial = super().get_initial(*args, **kwargs)
        return initial

    def form_valid(self, form):
        self.manager.variation_options.data = form.cleaned_data
        if 'goto' in self.request.POST and ':' in self.request.POST['goto']:
            return redirect(self.request.POST['goto'])
        if 'back' in self.request.POST:
            return redirect(self.manager.basic_info.url)
        else:
            return redirect(self.manager.variation_info.url)


class ListingOptions(BaseNewProductView):
    """View for the Listing Options page of the new product form."""

    template_name = 'inventory/new_product/listing_options.html'
    form_class = forms.ListingOptionsForm

    def get_initial(self, *args, **kwargs):
        initial = self.manager.listing_options.data
        if initial is None:
            initial = super().get_initial(*args, **kwargs)
        return initial

    def form_valid(self, form):
        self.manager.listing_options.data = form.cleaned_data
        if 'goto' in self.request.POST and ':' in self.request.POST['goto']:
            return redirect(self.request.POST['goto'])
        if 'back' in self.request.POST:
            return redirect('inventory:new_product_basic_info')
        else:
            return redirect('inventory:new_product_basic_info')


class BaseVariationProductView(BaseNewProductView):
    """Base class for variation pages of the new product form."""

    template_name = 'inventory/new_product/variation_info.html'

    def get_variation_options(self):
        variation_options = self.manager.variation_options.data
        return {
            key: value for key, value in variation_options.items()
            if len(value) > 0}

    def get_initial(self, *args, **kwargs):
        initial = self.get_variation_combinations(self.get_variation_options())
        for init in initial:
            init.update(self.manager.basic_info.data)
        return initial

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super().get_form_kwargs(*args, **kwargs)
        existing_data = self._get_existing_data()
        kwargs['form_kwargs'] = [{
            'existing_data': existing_data,
            'variation_options': v,
            } for v in self.get_variation_combinations(
                self.get_variation_options())]
        return kwargs

    def get_variation_combinations(self, variation_options):
        return list(
            dict(zip(variation_options, x)) for x in
            itertools.product(*variation_options.values()))

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['formset'] = context.pop('form')
        return context

    def form_valid(self, form):
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


class VariationInfo(BaseVariationProductView):
    """View for the Variation Info page of the new product form."""

    form_class = forms.VariationFormSet

    def _get_back_url(self):
        return self.manager.variation_options.url

    def _get_continue_url(self):
        return self.manager.variation_listing_options.url

    def _get_existing_data(self):
        return self.manager.variation_info.data

    def _save_form_data(self, data):
        self.manager.variation_info.data = data


class VariationListingOptions(BaseVariationProductView):
    """View for the Variation Listing Options page of the new product form."""

    form_class = forms.VariationListingOptionsFormSet

    def _get_back_url(self):
        return self.manager.variation_info.url

    def _get_continue_url(self):
        return self.manager.variation_info.url

    def _get_existing_data(self):
        return self.manager.variation_listing_options.data

    def _save_form_data(self, data):
        self.manager.variation_listing_options.data = data
