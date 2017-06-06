import json

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.edit import FormView
from django.core.urlresolvers import reverse_lazy

from . forms import NewSingleProductForm, NewVariationProductForm

from stcadmin import settings

import ccapi


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
        return super(NewSingleProductView, self).form_valid(form)


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


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_cloud_commerce_user)
@csrf_exempt
def api_product_search(request, search_text):
    cc_api = ccapi.CCAPI(settings.CC_LOGIN, settings.CC_PWD)
    search_result = cc_api.search_products(search_text)
    item_list = [
        {
            'id': item.id,
            'variation_id': item.variation_id,
            'sku': item.sku,
            'name': item.name,
            'thumnail': item.thumbnail} for item in search_result
    ]
    return HttpResponse(json.dumps(item_list))


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_cloud_commerce_user)
@csrf_exempt
def api_get_stock_for_product(request):
    cc_api = ccapi.CCAPI(settings.CC_LOGIN, settings.CC_PWD)
    variation_ids = json.loads(request.body)['variation_ids']
    stock_data = []
    for variation_id in variation_ids:
        product = cc_api.get_variation_by_id(variation_id)
        stock_data.append({
            'variation_id': variation_id,
            'stock_level': product.stock_level,
            'locations': ' '.join(
                [location.name for location in product.product.locations])
        })
    return HttpResponse(json.dumps(stock_data))


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_cloud_commerce_user)
@csrf_exempt
def api_get_new_sku(request):
    cc_api = ccapi.CCAPI(settings.CC_LOGIN, settings.CC_PWD)
    sku = cc_api.get_sku(range_sku=False)
    return HttpResponse(sku)


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_cloud_commerce_user)
@csrf_exempt
def api_get_new_range_sku(request):
    cc_api = ccapi.CCAPI(settings.CC_LOGIN, settings.CC_PWD)
    sku = cc_api.get_sku(range_sku=True)
    return HttpResponse(sku)


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_cloud_commerce_user)
@csrf_exempt
def api_update_stock_level(request):
    cc_api = ccapi.CCAPI(settings.CC_LOGIN, settings.CC_PWD)
    request_data = json.loads(request.body)
    product_id = request_data['product_id']
    new_stock_level = request_data['new_stock_level']
    old_stock_level = request_data['old_stock_level']
    cc_api.update_product_stock_level(
        product_id, new_stock_level, old_stock_level)
    product = cc_api.get_variation_by_id(product_id)
    stock_level = product.stock_level
    return HttpResponse(stock_level)
