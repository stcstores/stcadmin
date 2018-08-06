"""Template tags for the inventory app."""

from datetime import timedelta

import humanize
from django import template

register = template.Library()


@register.simple_tag
def humanize_time(time):
    """Return time or timedelta as a human readable string."""
    return humanize.naturaltime(time)


@register.simple_tag
def get_update_age(update):
    """Return the relative age of the update."""
    if update.finished is None:
        return "failed"
    time_since_update = update.time_since_update()
    if time_since_update < timedelta(minutes=5):
        return "recent"
    if time_since_update < timedelta(minutes=10):
        return "not_recent"
    else:
        return "old"
