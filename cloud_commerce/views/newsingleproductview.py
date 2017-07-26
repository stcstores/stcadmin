from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.edit import FormView
from cloud_commerce . forms import NewSingleProductForm
from django.shortcuts import redirect
from cloud_commerce.product_creator import SingleProduct


class NewSingleProductView(LoginRequiredMixin, FormView):
    template_name = 'cloud_commerce/single_product_form.html'
    form_class = NewSingleProductForm

    def old_form_valid(self, form):
        data = form.cleaned_data
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
        if len(form.cleaned_data['location']) > 0:
            self.set_bay(form)
        return redirect('cloud_commerce:product_range', self.range.id)

    def form_valid(self, form):
        new_product = SingleProduct(form.cleaned_data)
        return redirect(
            'inventory:product_range', new_product.product_range.id)
