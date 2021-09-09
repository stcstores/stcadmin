"""Template tags for the fba app."""

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def format_price(price):
    """Return integer pence as formated string."""
    if price is None:
        return mark_safe('<span class="negative">&mdash;</span>')
    elif price < 0:
        html_class = "negative"
    else:
        html_class = "neutral"
    string = '<span class="{html_class}">&pound;{price:.2f}</span>'
    return mark_safe(string.format(html_class=html_class, price=float(price / 100)))
