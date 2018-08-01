"""Template tags for the Reference app."""

from django import template
from stcadmin import settings
from django.utils.safestring import mark_safe

register = template.Library()

HELP_PATH = "{}help/html".format(settings.STATIC_URL)


@register.simple_tag
def help_url(page=None, anchor=None):
    """Return URL for help page."""
    if page is None:
        page = "index"
    url = HELP_PATH + "/{}.html".format(page)
    if anchor:
        anchor_slug = anchor.lower().replace(" ", "-")
        anchor_slug = anchor_slug.replace("_", "-")
        url = "{}#{}".format(url, anchor_slug)
    return url


@register.simple_tag
def help_button(page=None, anchor=None):
    """Return html for help button."""
    url = help_url(page, anchor)
    return mark_safe(
        '<a href="{}" target="_blank"><button class="help_button">Help'
        "</button></a>".format(url)
    )
