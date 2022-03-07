"""Template tags for the inventory app."""


from ccapi import URLs
from django import template

register = template.Library()
SUBDOMAIN = "seatontradingcompany"


@register.simple_tag
def ccp_product_range_page(range_id):
    """Return Cloud Commerce URL for a Product Range."""
    return URLs.range_url(SUBDOMAIN, range_id)


@register.simple_tag
def ccp_product_page(range_id, product_id):
    """Return Cloud Commerce URL for a Product."""
    return URLs.product_url(SUBDOMAIN, range_id, product_id)
