import json

from ccapi import URLs
from django import template
from django.utils.safestring import mark_safe
from inventory import models

register = template.Library()
SUBDOMAIN = 'seatontradingcompany'


@register.simple_tag
def ccp_product_range_page(range_id):
    return URLs.range_url(SUBDOMAIN, range_id)


@register.simple_tag
def ccp_product_page(range_id, product_id):
    return URLs.product_url(SUBDOMAIN, range_id, product_id)


@register.simple_tag
def warehouse_bays(warehouse=None):
    from ccapi import Warehouses
    if warehouse is None:
        return {x.name: x.bays for x in Warehouses}
    else:
        return Warehouses[warehouse].bays


@register.simple_tag
def product_options(option=None):
    from ccapi import ProductOptions
    if option is None:
        return {x.option_name: x.values for x in ProductOptions}
    else:
        return ProductOptions[option].options


@register.simple_tag
def shipping_price_data():
    lines = []
    shipping_prices = {}
    for price in models.ShippingPrice.objects.all():
        if price.country.name not in shipping_prices:
            shipping_prices[price.country.name] = []
        shipping_prices[price.country.name].append({
            'package_type': [p.name for p in price.package_type.all()],
            'min_weight': price.min_weight,
            'max_weight': price.max_weight,
            'item_price': price.item_price,
            'kilo_price': price.kilo_price,
        })
    lines.append(
        'var shipping_prices = {};'.format(json.dumps(shipping_prices)))
    lines.append(
        'var countries = {};'.format(json.dumps(
            [x.name for x in models.DestinationCountry.objects.all()])))
    lines.append(
        'var package_types = {};'.format(json.dumps(
            [x.name for x in models.PackageType.objects.all()])))
    return mark_safe('\n'.join(lines))
