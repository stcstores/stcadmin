"""Template tags for STCAdmin."""

from django import template

register = template.Library()


@register.simple_tag
def user_groups(user):
    """Return a list of names of groups to which user belongs."""
    groups = user.groups.values_list("name", flat=True)
    return groups


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
