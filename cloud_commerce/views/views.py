from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test

from stcadmin import settings

from ccapi import CCAPI


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
def product_range(request, range_id):
    product_range = CCAPI.get_range(range_id)
    return render(
        request, 'cloud_commerce/product_range.html',
        {'product_range': product_range})


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_cloud_commerce_user)
def print_statistics(request):
    user_list = CCAPI.get_users()
    print_jobs = CCAPI.get_print_queue()
    users = {}
    orders = []
    for job in print_jobs:
        order_id = job.order_id
        user_id = job.user_id
        if order_id in orders or order_id == 0:
            continue
        if user_id not in users:
            users[user_id] = 0
        users[user_id] += 1
    pack_count = {
        user_list[str(user_id)].full_name: count for user_id, count in
        users.items()}

    return render(
        request, 'cloud_commerce/print_statistics.html',
        {'pack_count': pack_count})
