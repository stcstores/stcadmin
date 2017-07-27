from django.shortcuts import render
from django.contrib.auth.decorators import login_required, user_passes_test

from stcadmin import settings

from ccapi import CCAPI


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
