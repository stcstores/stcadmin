from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse

from formtools.wizard.views import SessionWizardView

from . forms import NewSingleProductForm, NewVariationProductForm, \
    VariationChoicesForm, TempVariationForm, VariationFormSet

from stcadmin import settings

from ccapi import CCAPI
import time


def is_cloud_commerce_user(user):
    return user.groups.filter(name__in=['cloud_commerce'])


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_cloud_commerce_user)
def index(request):
    return render(request, 'cloud_commerce/index.html')


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_cloud_commerce_user)
def new_product(request):
    return render(request, 'cloud_commerce/new_product.html')


class NewProductView(FormView):
    success_url = reverse_lazy('cloud_commerce:index')

    def create_range(self, range_name, options):
        range_id = CCAPI.create_range(range_name)
        self.range = CCAPI.get_range(range_id)
        while self.range.id == 0:
            time.sleep(1)
            self.range = CCAPI.get_range(range_id)
        self.range = CCAPI.get_range(range_id)
        self.range.id = range_id
        for option in options:
            self.range.add_product_option(option)

    def create_product(
            self, name, barcode, description, vat_rate_id, weight, height,
            length, width, large_letter_compatible, stock_level, price,
            options):
        if len(description) == 0:
            description = name
        product = self.range.add_product(
            name, barcode, description=description, vat_rate_id=vat_rate_id)
        product.set_product_scope(
            weight, height, length, width, large_letter_compatible)
        product.set_stock_level(stock_level)
        product.set_handling_time(1)
        product.set_base_price(price)
        for option, value in options.items():
            if len(value) > 0:
                product.set_option_value(option, value, create=True)
        return product


class NewSingleProductView(LoginRequiredMixin, NewProductView):
    template_name = 'cloud_commerce/single_product_form.html'
    form_class = NewSingleProductForm

    def form_valid(self, form):
        data = form.cleaned_data
        CCAPI.create_session(settings.CC_LOGIN, settings.CC_PWD)
        options = self.get_options(form)
        self.create_range(data['title'].strip(), options.keys())
        large_letter_compatible = options['Package Type'] == 'Large Letter'
        self.product = self.create_product(
            name=data['title'].strip(),
            barcode=data['barcode'].strip(),
            description=data['description'].strip(),
            vat_rate_id=int(data['vat_rate']),
            weight=data['weight'],
            height=data['height'],
            length=data['length'],
            width=data['width'],
            large_letter_compatible=large_letter_compatible,
            stock_level=data['stock_level'],
            price=data['price'],
            options=options)
        return new_product_success(self.request, self.range, self.product)

    def get_options(self, form):
        required_options = {
            'Department': form.cleaned_data['department'].strip(),
            'Brand': form.cleaned_data['brand'].strip(),
            'Supplier SKU': form.cleaned_data['supplier_SKU'].strip(),
            'Manufacturer': form.cleaned_data['manufacturer'].strip(),
            'Supplier': form.cleaned_data['supplier'].strip(),
            'Purchase Price': form.cleaned_data['purchase_price'].strip(),
            'Package Type': form.cleaned_data['package_type']}
        optional_options = {
            key.replace('opt_', ''): value.strip() for key, value in
            form.cleaned_data.items() if key.startswith('opt_') and
            len(value.strip()) > 0}
        options = {**required_options, **optional_options}
        return options


class NewVariationProductView(LoginRequiredMixin, NewProductView):
    template_name = 'cloud_commerce/variation_product_form.html'
    form_class = NewVariationProductForm

    def form_valid(self, form):
        return super(NewVariationProductView, self).form_valid(form)


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_cloud_commerce_user)
def stock_manager(request):
    if request.method == 'GET' and len(request.GET) > 0:
        search_text = request.GET['stock_search']
        search_result = CCAPI.search_products(search_text)
        products = [
            CCAPI.get_product(result.variation_id) for result in search_result]
    else:
        search_text = ''
        products = []
    return render(
        request, 'cloud_commerce/stock_manager.html', {
            'products': products, 'search_text': search_text})


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_cloud_commerce_user)
def sku_generator(request):
    return render(request, 'cloud_commerce/sku_generator.html')


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_cloud_commerce_user)
def new_product_success(request, product_range, product):
    return render(
        request, 'cloud_commerce/new_product_success.html',
        {'product_range': product_range, 'product': product})


class VariationFormWizard(SessionWizardView):

    form_list = [
        NewVariationProductForm, VariationChoicesForm, VariationFormSet]

    TEMPLATES = {
        '0': 'cloud_commerce/variation_form_setup.html',
        '1': 'cloud_commerce/variation_option_value_form.html',
        '2': 'cloud_commerce/variation_table_form.html'}

    def get_template_names(self):
        print(self.steps.current)
        return [self.TEMPLATES[self.steps.current]]

    def post(self, *args, **kwargs):
        go_to_step = self.request.POST.get('wizard_goto_step', None)
        form = self.get_form(data=self.request.POST, files=self.request.FILES)

        current_index = self.get_step_index(self.steps.current)
        goto_index = self.get_step_index(go_to_step)

        if current_index > goto_index:
            if form.is_valid():
                self.storage.set_step_data(
                    self.steps.current,
                    self.process_step(form))
                self.storage.set_step_files(
                    self.steps.current,
                    self.process_step_files(form))
        return super().post(*args, **kwargs)

    def done(self, form_list, **kwargs):
        return HttpResponse(
            str(self.get_cleaned_data_for_step('3')))

    def get_form(self, step=None, data=None, files=None):
        form = super().get_form(step, data, files)
        if step is None:
            step = self.steps.current
        if step == '1':
            previous_data = self.get_cleaned_data_for_step('0')
            form.set_options(previous_data['selected_options'])
        if step == '2':
            if data is not None:
                data = self.remove_unused_variations(data)
            selected_options = self.get_selected_options()
            selected_variables = self.get_selected_variables()
            form.initial = self.initial_for_variation_table_form()
            for var_form in form.forms:
                var_form.set_variation_fields(
                    selected_options, selected_variables)
        return form

    def remove_unused_variations(self, data):
        selected_options = self.get_selected_options()
        forms = {}
        for key, value in data.items():
            if key[0] == '2' and key[2].isdigit():
                form_number = key.split('-')[1]
                field = key.split('-')[2]
                if field in selected_options:
                    if form_number not in forms:
                        forms[form_number] = {}
                    forms[form_number][field] = value
        print(forms)
        existant_variations = self.get_variations()
        fields_to_delete = []
        for form_number, variations in forms.items():
            for existing_variation in existant_variations:
                shared_items = set(
                    variations.items()) & set(existing_variation.items())
                if len(shared_items) == len(variations):
                    fields_to_delete += [
                        item for item in data if item[2] == form_number]
                    break
        return {
            key: value for key, value in data.items() if key not in
            fields_to_delete}

    def get_selected_options(self):
        return self.get_cleaned_data_for_step('0')['selected_options']

    def get_selected_variables(self):
        return self.get_cleaned_data_for_step('0')['selected_variables']

    def get_variations(self):
        return self.get_cleaned_data_for_step('1')['variations']

    def initial_for_variation_table_form(self):
        selected_variables = self.get_selected_variables()
        variations = self.get_variations()
        return [
            {**variation, **selected_variables} for variation in variations]
