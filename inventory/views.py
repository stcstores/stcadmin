from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.generic.edit import FormView

from stcadmin import settings

from ccapi import CCAPI
import json

from . forms import RangeSearchForm, LocationsFormSet


def is_inventory_user(user):
    return user.groups.filter(name__in=['inventory'])


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_inventory_user)
def index(request):
    return render(request, 'inventory/index.html')


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_inventory_user)
def product_range(request, range_id):
    product_range = CCAPI.get_range(range_id)
    return render(
        request, 'inventory/product_range.html',
        {'product_range': product_range})


class RangeSearch(FormView):
    template_name = 'inventory/range_search.html'
    form_class = RangeSearchForm

    def form_valid(self, form):
        return render(
            self.request, 'inventory/range_search.html', {
                'form': form,
                'product_ranges': form.ranges})


class LocationForm(FormView):

    template_name = 'inventory/locations.html'
    form_class = LocationsFormSet

    def post(self, request, range_id):
        if request.method == 'POST':
            formset = self.form_class(request.POST, request.FILES)
            if formset.is_valid():
                self.is_valid()
        else:
            formset = self.form_class(initial=self.get_initial())
        return render(request, self.template_name, {'formset': formset})

    def get(self, request, range_id):
        formset = self.form_class(initial=self.get_initial())
        return render(request, self.template_name, {'formset': formset})

    def get_initial(self):
        range_id = self.kwargs['range_id']
        product_range = CCAPI.get_range(range_id)
        products = product_range.products
        for product in products:
            product.bays = CCAPI.get_bays_for_product(product.id)
        initial = [
            {
                'product_id': product.id,
                'product_name': product.full_name,
                'locations': [bay.name for bay in product.bays],
            } for product in products]
        print(initial)
        return initial
