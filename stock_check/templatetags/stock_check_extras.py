from django import template
from stock_check import models

register = template.Library()


@register.simple_tag
def get_stock_level(product, bay):
    return models.ProductBay.objects.get(
        product=product.id, bay=bay.id).stock_level
