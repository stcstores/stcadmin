from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse_lazy

from . forms import NewSingleProductForm, NewVariationProductForm

from stcadmin import settings

from ccapi import CCAPI
import time


def is_cloud_commerce_user(user):
    return user.groups.filter(name__in=['cloud_commerce'])


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_cloud_commerce_user)
def index(request):
    return render(request, 'cloud_commerce/index.html')


def new_product(request):
    return render(request, 'cloud_commerce/new_product.html')


class NewSingleProductView(FormView):
    template_name = 'cloud_commerce/new_product_form.html'
    form_class = NewSingleProductForm
    success_url = reverse_lazy('cloud_commerce:index')

    def form_valid(self, form):
        CCAPI.create_session(settings.CC_LOGIN, settings.CC_PWD)
        self.create_range(form)
        self.create_product(form)
        self.create_options(form)
        return super(NewSingleProductView, self).form_valid(form)

    def create_range(self, form):
        range_name = form.cleaned_data['title'].strip()
        range_id = CCAPI.create_range(range_name)
        self.range = CCAPI.get_range(range_id)
        while self.range.id == 0:
            time.sleep(1)
            self.range = CCAPI.get_range(range_id)
        self.range = CCAPI.get_range(range_id)

    def create_product(self, form):
        name = form.cleaned_data['title'].strip()
        barcode = form.cleaned_data['barcode'].strip()
        description = form.cleaned_data['description'].strip()
        vat_rate_id = int(form.cleaned_data['vat_rate'])
        self.product = self.range.add_product(
            name, barcode, description=description, vat_rate_id=vat_rate_id)
        large_letter_compatible = form.cleaned_data[
            'package_type'] == 'Large Letter'
        self.product.set_product_scope(
            weight=form.cleaned_data['weight'],
            height=form.cleaned_data['height'],
            length=form.cleaned_data['length'],
            width=form.cleaned_data['width'],
            large_letter_compatible=large_letter_compatible)
        self.product.set_stock_level(form.cleaned_data['stock_level'])
        self.product.set_handling_time(1)
        self.product.set_base_price(form.cleaned_data['price'])

    def create_options(self, form):
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
        for option in options:
            self.range.add_product_option(option)
        for option, value in options.items():
            if len(value) > 0:
                self.product.set_option_value(option, value, create=True)


class NewVariationProductView(FormView):
    template_name = 'cloud_commerce/new_product_form.html'
    form_class = NewVariationProductForm
    success_url = reverse_lazy('cloud_commerce:index')

    def form_valid(self, form):
        return super(NewVariationProductView, self).form_valid(form)


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_cloud_commerce_user)
def stock_manager(request):
    return render(request, 'cloud_commerce/stock_manager.html')


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_cloud_commerce_user)
def sku_generator(request):
    return render(request, 'cloud_commerce/sku_generator.html')
