from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test

from stcadmin import settings

from ccapi import CCAPI


def is_inventory_user(user):
    return user.groups.filter(name__in=['inventory'])


def get_ranges(search_text):
    search_result = CCAPI.search_products(search_text)
    range_ids = list(set([result.id for result in search_result]))
    ranges = [CCAPI.get_range(range_id) for range_id in range_ids]
    print(dir(ranges[0].products[0]))
    return ranges


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


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_inventory_user)
def range_search(request):
    if request.method == 'GET' and 'search_text' in request.GET:
        search_text = request.GET['search_text']
        ranges = get_ranges(search_text)
    else:
        ranges = []
    return render(
        request, 'inventory/range_search.html', {'product_ranges': ranges})
