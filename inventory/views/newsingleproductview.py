"""Views for creating new products."""

import itertools

from django.shortcuts import redirect
from django.views.generic.edit import FormView

from inventory import forms

from .views import InventoryUserMixin


class NewProductManager:
    """Access new product data stored in session."""

    VARIATION = 'variation'
    SINGLE = 'single'
    NEW_PRODUCT = 'new_product_data'
    BASIC = 'basic'
    TYPE = 'type'
    VARIATION_OPTIONS = 'variation_options'
    LISTING_OPTIONS = 'listing_options'
    VARIATION_DATA = 'variation_data'
    VARIATION_LISTING_OPTIONS = 'variation_listing_options'

    def __init__(self, request):
        self.request = request
        self.session = request.session
        self.request.session.modified = True
        self.new_product_data = request.session.get(self.NEW_PRODUCT, None)
        if self.new_product_data is not None:
            self.basic = self.new_product_data.get(self.BASIC, None)
            self.product_type = self.new_product_data.get(self.TYPE, None)
            self.variation_options = self.new_product_data.get(
                self.VARIATION_OPTIONS, None)
            self.listing_options = self.new_product_data.get(
                self.LISTING_OPTIONS, None)
            self.variation_data = self.new_product_data.get(
                self.VARIATION_DATA, None)
            self.variation_listing_options = self.new_product_data.get(
                self.VARIATION_LISTING_OPTIONS, None)


class NewProductView(InventoryUserMixin, FormView):

    def dispatch(self, *args, **kwargs):
        self.new_product_manager = NewProductManager(args[0])
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['product_data'] = self.new_product_manager
        return context


class NewProductBasicView(NewProductView):
    template_name = 'inventory/new_product/single_product_form.html'
    form_class = forms.NewProductBasicForm

    def get_initial(self, *args, **kwargs):
        existing_data = self.new_product_manager.basic
        if existing_data is not None:
            initial = existing_data
        else:
            initial = super().get_initial(*args, **kwargs)
        return initial

    def form_valid(self, form):
        self.new_product_manager.basic = form.cleaned_data
        if 'variations' in self.request.POST:
            self.new_product_manager.product_type = NewProductManager.VARIATION
            return redirect('inventory:variation_options')
        else:
            self.new_product_manager.product_type = NewProductManager.SINGLE
            return redirect('inventory:listing_options')


class VariationOptionsView(NewProductView):
    template_name = 'inventory/new_product/variation_options.html'
    form_class = forms.VariationOptionsForm

    def get_initial(self, *args, **kwargs):
        initial = self.new_product_manager.variation_options
        if initial is None:
            initial = super().get_initial(*args, **kwargs)
        return initial

    def form_valid(self, form):
        self.new_product_manager.variation_options = form.cleaned_data
        if 'back' in self.request.POST:
            return redirect('inventory:new_product')
        else:
            return redirect('inventory:new_product_variations')


class ListingOptionsView(NewProductView):
    template_name = 'inventory/new_product/single_product_form.html'
    form_class = forms.ListingOptionsForm

    def get_initial(self, *args, **kwargs):
        initial = self.new_product_manager.listing_options
        if initial is None:
            initial = super().get_initial(*args, **kwargs)
        return initial

    def form_valid(self, form):
        self.new_product_manager.listing_options = form.cleaned_data
        if 'back' in self.request.POST:
            return redirect('inventory:new_product')
        else:
            return redirect('')


class BaseVariationProductView(NewProductView):
    template_name = 'inventory/new_product/variations.html'

    def get_variation_options(self):
        variation_options = self.new_product_manager.variation_options
        return {
            key: value for key, value in variation_options.items()
            if len(value) > 0}

    def get_initial(self, *args, **kwargs):
        initial = self.get_variation_combinations(self.get_variation_options())
        for init in initial:
            init.update(self.new_product_manager.basic)
        return initial

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super().get_form_kwargs(*args, **kwargs)
        existing_data = self.get_existing_data()
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
        self.save_form_data(form.cleaned_data)
        if 'back' in self.request.POST:
            return redirect(self.back_page)
        else:
            return redirect(self.continue_page)

    def get_existing_data(self):
        raise NotImplementedError()

    def save_form_data(self, data):
        raise NotImplementedError()


class NewProductVariationsView(BaseVariationProductView):

    form_class = forms.VariationFormSet
    back_page = 'inventory:variation_options'
    continue_page = 'inventory:variation_listing_options'

    def get_existing_data(self):
        return self.new_product_manager.variation_data

    def save_form_data(self, data):
        self.new_product_manager.variation_data = data


class VariationListingOptionsView(BaseVariationProductView):

    form_class = forms.VariationListingOptionsFormSet
    back_page = 'inventory:new_product_variations'
    continue_page = 'inventory:new_product_variations'

    def get_existing_data(self):
        return self.new_product_manager.variation_listing_options

    def save_form_data(self, data):
        self.new_product_manager.variation_listing_options = data
