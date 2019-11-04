"""Template tags for STCAdmin."""

from django import template
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.safestring import SafeString

register = template.Library()


@register.simple_tag
def tooltip(title="", text=""):
    """Return HTML for tooltip."""
    rendered_template = render_to_string(
        "home/tooltip.html", {"title": title, "text": text}
    )
    return SafeString(rendered_template)


@register.simple_tag
def user_groups(user):
    """Return a list of names of groups to which user belongs."""
    groups = user.groups.values_list("name", flat=True)
    return groups


@register.simple_tag
def tooltip_help_text(field):
    """Return rendered tooltip for a form field."""
    if field is not None and len(field.help_text) > 0:
        return tooltip(field.label, field.help_text)
    return ""


@register.simple_tag
def scayt_customer_id():
    """Return the SCAYT customer ID."""
    return settings.SCAYT_CUSTOMER_ID
