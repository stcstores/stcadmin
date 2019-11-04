"""Template tags for print_audit."""
from django import template
from django.utils.safestring import mark_safe
from django.utils.timezone import now

from print_audit import models

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


@register.simple_tag
def feedback_badges(user):
    """Return rendered feedback badges."""
    try:
        user = models.CloudCommerceUser.objects.filter(stcadmin_user=user)[0]
    except Exception:
        return ""
    feedback_types = models.Feedback.objects.all().order_by("-score")
    html = ["<table>"]
    for feedback_type in feedback_types:
        count = models.UserFeedback.objects.filter(
            user=user.pk, timestamp__month=now().month, feedback_type=feedback_type
        ).count()
        html.append(
            '<td><img src="{}" alt="{}" height="15">'.format(
                feedback_type.image.url, feedback_type.name
            )
        )
        html.append("&nbsp;{}</td>".format(count))
    html.append("</table>")
    return mark_safe("\n".join(html))
