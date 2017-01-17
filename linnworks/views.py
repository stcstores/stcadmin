import json
import copy

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
    def get_sku_lookup(linking_table):
        channels = list(set(linking_table.get_column('Sub Source')))
        SKUs = {}
        blank_sku_data = {channel: [] for channel in channels}
        for row in linking_table:
            linn_sku = row['StockSKU']
            if linn_sku not in SKUs:
                SKUs[linn_sku] = copy.deepcopy(blank_sku_data)
            SKUs[linn_sku][row['Sub Source']].append(row['ChannelSKU'])
        return SKUs

    pylinnworks.PyLinnworks.connect(config=PYLINNWORKS_CONFIG)
    linking_table = pylinnworks.Export.get_linking()
    sku_lookup = get_sku_lookup(linking_table)
    sku_lookup_string = json.dumps(
        sku_lookup, indent=4, separators=(',', ': '))
    return render(request, 'linnworks/sku_converter.html', {
        'lookup_data': sku_lookup_string})
