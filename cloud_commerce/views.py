import json

from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse
from django.shortcuts import redirect
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views import View

from stcadmin import settings

import ccapi


def is_cloud_commerce_user(user):
    return user.groups.filter(name__in=['cloud_commerce'])


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_cloud_commerce_user)
def index(request):
    return render(request, 'cloud_commerce/index.html')


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_cloud_commerce_user)
def stock_manager(request):
    return render(request, 'cloud_commerce/stock_manager.html')


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_cloud_commerce_user)
def api_product_search(request, search_text):
    cc_api = ccapi.CloudCommerceAPISession
    cc_api.get_session(settings.CC_LOGIN, settings.CC_PWD)
    search_result = ccapi.DoSearch(search_text)
    item_list = [
        {
            'id': item.id,
            'variation_id': item.variation_id,
            'sku': item.sku,
            'name': item.name,
            'thumnail': item.thumbnail} for item in search_result
    ]
    return HttpResponse(json.dumps(item_list))
