"""Template tags for print_audit."""

from django import template

register = template.Library()


@register.simple_tag
def dict_key(dictionary, *args):
    """Return value dictonary[args-1]."""
    for key in args:
        dictionary = dictionary[key]
    return dictionary


@register.simple_tag
def feedback_count(user, feedback):
    """Return number of Feedbacks of type feedback for User user."""
    return user.feedback_count(feedback)
