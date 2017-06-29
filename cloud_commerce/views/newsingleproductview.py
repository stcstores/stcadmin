from django.contrib.auth.mixins import LoginRequiredMixin
from . newproductview import NewProductView
from cloud_commerce . forms import NewSingleProductForm
from stcadmin import settings
from ccapi import CCAPI
from django.shortcuts import redirect


class NewSingleProductView(LoginRequiredMixin, NewProductView):
    template_name = 'cloud_commerce/single_product_form.html'
    form_class = NewSingleProductForm

    def form_valid(self, form):
        data = form.cleaned_data
        CCAPI.create_session(settings.CC_LOGIN, settings.CC_PWD)
        options = self.get_options(form)
        self.create_range(data['title'], options.keys())
        large_letter_compatible = options['Package Type'] == 'Large Letter'
        self.product = self.create_product(
            name=data['title'],
            barcode=data['barcode'],
            description=data['description'],
            vat_rate_id=int(data['vat_rate']),
            weight=data['weight'],
            height=data['height'],
            length=data['length'],
            width=data['width'],
            large_letter_compatible=large_letter_compatible,
            stock_level=data['stock_level'],
            price=data['price'],
            options=options)
        return redirect('cloud_commerce:product_range', self.range.id)

    def get_options(self, form):
        required_options = {
            'Department': form.cleaned_data['department'],
            'Brand': form.cleaned_data['brand'],
            'Supplier SKU': form.cleaned_data['supplier_SKU'],
            'Manufacturer': form.cleaned_data['manufacturer'],
            'Supplier': form.cleaned_data['supplier'],
            'Purchase Price': form.cleaned_data['purchase_price'],
            'Package Type': form.cleaned_data['package_type']}
        optional_options = {
            key.replace('opt_', ''): value for key, value in
            form.cleaned_data.items() if key.startswith('opt_') and
            len(value) > 0}
        options = {**required_options, **optional_options}
        return options
