"""Template tags for the fba app."""

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def format_price(price):
    """Return integer pence as formated string."""
    if price is None:
        return mark_safe('<span class="text-danger">&mdash;</span>')
    elif price < 0:
        html_class = "text-danger"
    else:
        html_class = "text-dark"
    string = '<span class="{html_class}">&pound;{price:.2f}</span>'
    return mark_safe(string.format(html_class=html_class, price=float(price / 100)))
