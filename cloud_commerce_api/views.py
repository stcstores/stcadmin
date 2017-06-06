import json

from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.csrf import csrf_exempt

from stcadmin import settings
from cloud_commerce.views import is_cloud_commerce_user

from ccapi import CCAPI


CCAPI.create_session(settings.CC_LOGIN, settings.CC_PWD)


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_cloud_commerce_user)
@csrf_exempt
def product_search(request, search_text):
    search_result = CCAPI.search_products(search_text)
    item_list = [
        {
            'id': item.id,
            'variation_id': item.variation_id,
            'sku': item.sku,
            'name': item.name,
            'thumnail': item.thumbnail} for item in search_result]
    return HttpResponse(json.dumps(item_list))


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_cloud_commerce_user)
@csrf_exempt
def get_stock_for_product(request):
    variation_ids = json.loads(request.body)['variation_ids']
    stock_data = []
    for variation_id in variation_ids:
        product = CCAPI.get_variation_by_id(variation_id)
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
def get_new_sku(request):
    sku = CCAPI.get_sku(range_sku=False)
    return HttpResponse(sku)


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_cloud_commerce_user)
@csrf_exempt
def get_new_range_sku(request):
    sku = CCAPI.get_sku(range_sku=True)
    return HttpResponse(sku)


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_cloud_commerce_user)
@csrf_exempt
def update_stock_level(request):
    request_data = json.loads(request.body)
    product_id = request_data['product_id']
    new_stock_level = request_data['new_stock_level']
    old_stock_level = request_data['old_stock_level']
    CCAPI.update_product_stock_level(
        product_id, new_stock_level, old_stock_level)
    product = CCAPI.get_variation_by_id(product_id)
    stock_level = product.stock_level
    return HttpResponse(stock_level)
