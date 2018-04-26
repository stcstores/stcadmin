"""Template tags for the inventory app."""

import json

from ccapi import URLs
from django import template
from django.utils.safestring import mark_safe

from inventory import models

register = template.Library()
SUBDOMAIN = 'seatontradingcompany'


@register.simple_tag
def ccp_product_range_page(range_id):
    """Return Cloud Commerce URL for a Product Range."""
    return URLs.range_url(SUBDOMAIN, range_id)


@register.simple_tag
def ccp_product_page(range_id, product_id):
    """Return Cloud Commerce URL for a Product."""
    return URLs.product_url(SUBDOMAIN, range_id, product_id)


@register.simple_tag
def ccp_order_page(order_id, customer_id):
    """Return Cloud Commerce URL for a order."""
    return URLs.order_url(SUBDOMAIN, order_id, customer_id)


@register.simple_tag
def warehouses():
    """Return dict containing Warehouses and bays."""
    warehouses = models.Warehouse.used_warehouses.all()
    data = {}
    for w in warehouses:
        data[w.warehouse_id] = [
            {'value': b.bay_id, 'text': b.name} for b in w.bay_set.all()]
    return mark_safe(json.dumps(data))


@register.simple_tag
def product_options(option=None):
    """Return dict containing product options and values."""
    from ccapi import ProductOptions
    if option is None:
        return {x.option_name: x.values for x in ProductOptions}
    else:
        return ProductOptions[option].options
