"""Template tags for the Order app."""

from django import template
from django.utils.safestring import mark_safe

SUBDOMAIN = "seatontradingcompany"

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


@register.simple_tag
def format_percentage(percentage):
    """Return a coloured percentage value."""
    if percentage is None:
        return ""
    if percentage <= 0:
        html_class = "error"
    elif percentage <= 10:
        html_class = "warning"
    else:
        html_class = "success"
    return mark_safe(f"<span class={html_class!r}>{percentage}%</span>")
