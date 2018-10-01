"""Template tags for the Stock Check app."""

from django import template
from stock_check import models

register = template.Library()


@register.simple_tag
def get_stock_level(product, bay):
    """Return the quantity of product in bay."""
    return models.ProductBay.objects.get(product=product.id, bay=bay.id).stock_level
