"""Template tags for STCAdmin."""

from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def user_groups(user):
    """Return a list of names of groups to which user belongs."""
    groups = user.groups.values_list("name", flat=True)
    return groups


@register.simple_tag
def scayt_customer_id():
    """Return the SCAYT customer ID."""
    return settings.SCAYT_CUSTOMER_ID


@register.filter
def add_class(field, css_class):
    """Add a CSS class to a form field."""
    classes = field.field.widget.attrs.get("class", "")
    field.field.widget.attrs["class"] = " ".join((classes, css_class)).strip()
    return field


@register.simple_tag(takes_context=True)
def query_transform(context, **kwargs):
    """
    Update request parameters.

    Used to preserve other GET parameters when creating a pagination link.
    """
    query = context["request"].GET.copy()
    for key, value in kwargs.items():
        query[key] = value
    return query.urlencode()
