from django.shortcuts import render, HttpResponse
from stcadmin.settings import PYLINNWORKS_CONFIG
import pylinnworks


def index(request):
    return render(request, 'linnworks/index.html')


def manifest(request):
    pylinnworks.PyLinnworks.connect(config=PYLINNWORKS_CONFIG)
    consignments = pylinnworks.Shipping.get_manifest_consignments()
    return render(
        request, 'linnworks/manifest.html',
        {'consignments': consignments})


def cancel_order(request):
    order_id = request.POST['order_id']
    return HttpResponse(order_id)
