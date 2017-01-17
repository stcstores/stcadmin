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


def cancel_consignment(request):
    pylinnworks.PyLinnworks.connect(config=PYLINNWORKS_CONFIG)
    consignments = pylinnworks.Shipping.get_manifest_consignments()
    for consignment in consignments:
        if int(consignment.order_id) == int(request.POST['order_id']):
            return HttpResponse(str(consignment))
    return HttpResponse('Order Not Found', status=400)


def sku_converter(request):
    return render(request, 'linnworks/sku_converter.html')
