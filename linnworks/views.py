import json

from stcadmin import settings
from django.shortcuts import render, HttpResponse, redirect
from stcadmin.settings import PYLINNWORKS_CONFIG
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import Http404
from . forms import EditItemForm, NewItemForm

import pylinnworks


def is_linnworks_user(user):
    return user.groups.filter(name__in=['linnworks'])


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_linnworks_user)
def index(request):
    return render(request, 'linnworks/index.html')


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_linnworks_user)
def manifest(request):
    pylinnworks.PyLinnworks.connect(config=PYLINNWORKS_CONFIG)
    consignments = pylinnworks.Shipping.get_manifest_consignments()
    return render(
        request, 'linnworks/manifest.html',
        {'consignments': consignments})


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_linnworks_user)
def cancel_consignment(request):
    pylinnworks.PyLinnworks.connect(config=PYLINNWORKS_CONFIG)
    consignments = pylinnworks.Shipping.get_manifest_consignments()
    for consignment in consignments:
        if int(consignment.order_id) == int(request.POST['order_id']):
            consignment.cancel()
            return HttpResponse(str(consignment))
    return HttpResponse('Order Not Found', status=400)


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_linnworks_user)
def sku_converter(request):
    pylinnworks.PyLinnworks.connect(config=PYLINNWORKS_CONFIG)
    channels = pylinnworks.Linking()
    return render(
        request, 'linnworks/sku_converter.html', {'channels': channels})


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_linnworks_user)
def get_linked_for_channel_sku(request):
    channel_id = int(request.POST['channel_id'])
    channel_sku = request.POST['channel_sku']
    pylinnworks.PyLinnworks.connect(config=PYLINNWORKS_CONFIG)
    channel = pylinnworks.Linking.get_channel_by_ID(channel_id)
    items = channel.get_items(keyword=channel_sku)
    data = [{
        'linnworks_sku': item.linked_item_sku, 'stock_id': item.linked_item_id,
        'linnworks_title': item.linked_item_title,
        'channel_title': item.title} for item in items]
    return HttpResponse(json.dumps(data))


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_linnworks_user)
def inventory_item(request, stock_id):
    if request.method == 'POST':
        form = EditItemForm(request.POST, stock_id=stock_id)
        if form.is_valid():
            form.save()
            redirect('linnworks:inventory_item', stock_id)
    else:
        try:
            form = EditItemForm(stock_id=stock_id)
        except:
            raise Http404
    return render(request, 'linnworks/inventory_item.html', {'form': form})


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_linnworks_user)
def search_inventory(request):
    pylinnworks.PyLinnworks.connect(config=PYLINNWORKS_CONFIG)
    if request.method == 'POST':
        items = pylinnworks.Inventory.search_by_SKU(
            request.POST['search_term'])
    else:
        items = []
    return render(request, 'linnworks/search_inventory.html', {'items': items})


@login_required(login_url=settings.LOGIN_URL)
@user_passes_test(is_linnworks_user)
def new_item(request):
    if request.method == 'POST':
        form = NewItemForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect(
                'linnworks:inventory_item', form.cleaned_data['stock_id'])
    else:
        form = NewItemForm()
    return render(request, 'linnworks/new_item.html', {'form': form})
