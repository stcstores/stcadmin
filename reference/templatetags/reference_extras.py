"""Template tags for the Reference app."""

from django import template
from stcadmin import settings
register = template.Library()

HELP_PATH = '{}help/html'.format(settings.STATIC_URL)


@register.simple_tag
def help_url(page, anchor=None):
    """Return URL for help page."""
    url = HELP_PATH + '/{}.html'.format(page)
    if anchor:
        anchor_slug = anchor.lower().replace(' ', '-')
        url = '{}#{}'.format(url, anchor_slug)
    return url
