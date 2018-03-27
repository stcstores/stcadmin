"""Views for creating new products."""

import itertools

from django.shortcuts import redirect
from django.views.generic.edit import FormView, View

from inventory import forms

from .views import InventoryUserMixin


class Page:
    def __init__(self, name, identifier, manager, url=None):
        self.name = name
        self.identifier = identifier
        if url is None:
            self.url = 'inventory:new_product_{}'.format(self.identifier)
        else:
            self.url = 'inventory:{}'.format(url)
        self.manager = manager

    @property
    def data(self):
        data = self.manager.session[self.manager.NEW_PRODUCT].get(
            self.identifier, None)
        return data

    @data.setter
    def data(self, data):
        self.manager.session[self.manager.NEW_PRODUCT][self.identifier] = data
        self.manager.session.modified = True


class NewProductManager:
    """Access new product data stored in session."""

    VARIATION = 'variation'
    SINGLE = 'single'
    NEW_PRODUCT = 'new_product_data'
    BASIC = 'basic'
    TYPE = 'type'
    VARIATION_OPTIONS = 'variation_options'
    LISTING_OPTIONS = 'listing_options'
    VARIATION_DATA = 'variations'
    VARIATION_LISTING_OPTIONS = 'variation_listing_options'

    def __init__(self, request):
        self.request = request
        self.session = request.session
        if self.NEW_PRODUCT not in self.session:
            self.session[self.NEW_PRODUCT] = {}
        self.session.modified = True
        self.basic = Page('Baisic Info', self.BASIC, self, url='new_product')
        self.listing_options = Page(
            'Listing Options', self.LISTING_OPTIONS, self)
        self.variation_options = Page(
            'Variation Options', self.VARIATION_OPTIONS, self)
        self.variations = Page('Variation Info', self.VARIATION_DATA, self)
        self.variation_listing_options = Page(
            'Variation Listing Options', self.VARIATION_LISTING_OPTIONS, self)
        self.data = self.session.get(self.NEW_PRODUCT, None)
        self.pages = (
            self.basic, self.listing_options, self.variation_options,
            self.variations, self.variation_listing_options)
        self.single_product_pages = (self.basic, self.listing_options)
        self.variation_product_pages = (
            self.basic, self.variation_options, self.variations,
            self.variation_listing_options)
        if self.product_type == self.VARIATION:
            self.current_pages = self.variation_product_pages
        elif self.product_type == self.SINGLE:
            self.current_pages = self.single_product_pages
        else:
            self.current_pages = (self.basic, )

    @property
    def product_type(self):
        product_data = self.session.get(self.NEW_PRODUCT, None)
        if product_data is not None:
            return product_data.get(self.TYPE, None)
        else:
            return None

    @product_type.setter
    def product_type(self, product_type):
        product_data = self.session.get(self.NEW_PRODUCT, None)
        product_data[self.TYPE] = product_type
        self.session.modified = True

    def delete_product(self):
        self.session[self.NEW_PRODUCT] = {}


class DeleteProduct(InventoryUserMixin, View):

    def dispatch(self, *args, **kwargs):
        self.manager = NewProductManager(args[0])
        self.manager.delete_product()
        return redirect('inventory:new_product')


class NewProductView(InventoryUserMixin, FormView):

    def dispatch(self, *args, **kwargs):
        self.manager = NewProductManager(args[0])
        return super().dispatch(*args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context['manager'] = self.manager
        return context


class NewProductBasicView(NewProductView):
    template_name = 'inventory/new_product/single_product_form.html'
    form_class = forms.NewProductBasicForm

    def get_initial(self, *args, **kwargs):
        existing_data = self.manager.basic.data
        if existing_data is not None:
            initial = existing_data
        else:
            initial = super().get_initial(*args, **kwargs)
        return initial

    def form_valid(self, form):
        self.manager.basic.data = form.cleaned_data
        if 'goto' in self.request.POST and ':' in self.request.POST['goto']:
            return redirect(self.request.POST['goto'])
        if 'variations' in self.request.POST:
            self.manager.product_type = NewProductManager.VARIATION
            return redirect(self.manager.variation_options.url)
        else:
            self.manager.product_type = NewProductManager.SINGLE
            return redirect(self.manager.listing_options.url)


class VariationOptionsView(NewProductView):
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
            return redirect(self.manager.basic.url)
        else:
            return redirect(self.manager.variations.url)


class ListingOptionsView(NewProductView):
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
            return redirect('inventory:new_product')
        else:
            return redirect('inventory:new_product')


class BaseVariationProductView(NewProductView):
    template_name = 'inventory/new_product/variations.html'

    def get_variation_options(self):
        variation_options = self.manager.variation_options.data
        return {
            key: value for key, value in variation_options.items()
            if len(value) > 0}

    def get_initial(self, *args, **kwargs):
        initial = self.get_variation_combinations(self.get_variation_options())
        for init in initial:
            init.update(self.manager.basic.data)
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
        if 'goto' in self.request.POST and ':' in self.request.POST['goto']:
            return redirect(self.request.POST['goto'])
        if 'back' in self.request.POST:
            return redirect(self.get_back_url())
        else:
            return redirect(self.get_continue_url())

    def get_existing_data(self):
        raise NotImplementedError()

    def save_form_data(self, data):
        raise NotImplementedError()

    def get_back_url(self):
        raise NotImplementedError()

    def get_continue_url(self):
        raise NotImplementedError()


class NewProductVariationsView(BaseVariationProductView):

    form_class = forms.VariationFormSet

    def get_back_url(self):
        return self.manager.variation_options.url

    def get_continue_url(self):
        return self.manager.variation_listing_options.url

    def get_existing_data(self):
        return self.manager.variations.data

    def save_form_data(self, data):
        self.manager.variations.data = data


class VariationListingOptionsView(BaseVariationProductView):

    form_class = forms.VariationListingOptionsFormSet

    def get_back_url(self):
        return self.manager.variations.url

    def get_continue_url(self):
        return self.manager.variations.url

    def get_existing_data(self):
        return self.manager.variation_listing_options.data

    def save_form_data(self, data):
        self.manager.variation_listing_options.data = data
