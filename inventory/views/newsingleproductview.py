import itertools

from django.shortcuts import redirect
from django.views.generic.edit import FormView

from inventory import forms

from .views import InventoryUserMixin


class NewProductView(InventoryUserMixin, FormView):

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['product_data'] = self.request.session['new_product_data']
        return context


class NewProductBasicView(NewProductView):
    template_name = 'inventory/new_product/single_product_form.html'
    form_class = forms.NewProductBasicForm

    def get_initial(self, *args, **kwargs):
        if 'new_product_data' in self.request.session:
            initial = self.request.session['new_product_data']['basic']
        else:
            initial = super().get_initial(*args, **kwargs)
        return initial

    def form_valid(self, form):
        self.request.session['new_product_data']['basic'] = form.cleaned_data
        self.request.session.modified = True
        if 'variations' in self.request.POST:
            return redirect('inventory:variation_options')
        else:
            return redirect('single_product_options')


class VariationOptionsView(NewProductView):
    template_name = 'inventory/new_product/variation_options.html'
    form_class = forms.VariationOptionsForm

    def get_initial(self, *args, **kwargs):
        try:
            initial = self.request.session[
                'new_product_data']['variation_options']
        except KeyError:
            initial = super().get_initial(*args, **kwargs)
        return initial

    def form_valid(self, form):
        self.request.session[
            'new_product_data']['variation_options'] = form.cleaned_data
        self.request.session.modified = True
        if 'back' in self.request.POST:
            return redirect('inventory:new_product')
        else:
            return redirect('inventory:new_product_variations')


class BaseVariationProductView(NewProductView):
    template_name = 'inventory/new_product/variations.html'

    def get_variation_options(self):
        variation_options = self.request.session[
            'new_product_data']['variation_options']
        return {
            key: value for key, value in variation_options.items()
            if len(value) > 0}

    def get_initial(self, *args, **kwargs):
        initial = self.get_variation_combinations(self.get_variation_options())
        for init in initial:
            init.update(self.request.session['new_product_data']['basic'])
        return initial

    def get_form_kwargs(self, *args, **kwargs):
        kwargs = super().get_form_kwargs(*args, **kwargs)
        existing_data = self.request.session['new_product_data'].get(
            self.existing_data_key, None)
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
        self.request.session[
            'new_product_data'][self.existing_data_key] = form.cleaned_data
        self.request.session.modified = True
        if 'back' in self.request.POST:
            return redirect(self.back_page)
        else:
            return redirect(self.continue_page)


class NewProductVariationsView(BaseVariationProductView):

    form_class = forms.VariationFormSet
    existing_data_key = 'variation_data'
    back_page = 'inventory:variation_options'
    continue_page = 'inventory:variation_listing_options'


class VariationListingOptionsView(BaseVariationProductView):

    form_class = forms.VariationListingOptionsFormSet
    existing_data_key = 'variation_listing_options'
    back_page = 'inventory:new_product_variations'
    continue_page = 'inventory:new_product_variations'
