from ccapi import CCAPI
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render
from stcadmin import settings

from home.views import UserInGroupMixin


def is_cloud_commerce_user(user):
    return user.groups.filter(name__in=['cloud_commerce'])


class CloudCommerceUserMixin(UserInGroupMixin):
    groups = ['cloud_commerce']


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
def sku_generator(request):
    return render(request, 'cloud_commerce/sku_generator.html')


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_cloud_commerce_user)
def product_range(request, range_id):
    product_range = CCAPI.get_range(range_id)
    return render(
        request, 'cloud_commerce/product_range.html',
        {'product_range': product_range})
