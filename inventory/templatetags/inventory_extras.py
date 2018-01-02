from ccapi import CCAPI, URLs
from django import template

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
    warehouses = CCAPI.get_warehouses()
    if warehouse is None:
        return {x.name: x.bays for x in warehouses}
    else:
        return warehouses[warehouse].bays


@register.simple_tag
def product_options(option=None):
    from ccapi import ProductOptions
    if option is None:
        return {x.option_name: x.values for x in ProductOptions}
    else:
        return ProductOptions[option].options
