import json

from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt
from stcadmin import settings

from ccapi import CCAPI


def is_epos_user(user):
    return user.groups.filter(name__in=['epos'])


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_epos_user)
def index(request):
    return render(request, 'epos/index.html')


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_epos_user)
@csrf_exempt
def barcode_search(request):
    if request.method == 'POST':
        barcode = request.POST['barcode']
        search_result = CCAPI.search_products(barcode)
        if len(search_result) == 0:
            return HttpResponse('Not Found')
        product = search_result[0]
        product_id = str(search_result[0].variation_id)
        product = CCAPI.get_product(product_id)
        data = {
            'id': product.id,
            'name': product.full_name,
            'sku': product.sku,
            'barcode': product.barcode,
            'base_price': float(product.base_price),
            'vat_rate': int(product.vat_rate.replace('%', '')),
            'stock_level': product.stock_level,
            'order_quantity': 1,
        }
        return HttpResponse(json.dumps(data))


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_epos_user)
@csrf_exempt
def epos_order(request):
    if request.method == 'POST':
        products = json.loads(request.body)
        for product_id, product in products.items():
            old_stock_level = product['stock_level']
            new_stock_level = product[
                'stock_level'] - product['order_quantity']
            CCAPI.update_product_stock_level(
                product_id, new_stock_level, old_stock_level)
        return HttpResponse('ok')
