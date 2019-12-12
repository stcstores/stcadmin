"""Template tags for the Feedback app."""
from django import template
from django.db.models import Count, Q
from django.utils.safestring import mark_safe
from django.utils.timezone import now

from feedback import models

register = template.Library()


@register.simple_tag
def feedback_badges(user):
    """Return rendered feedback badges."""
    feedback_types = models.Feedback.objects.annotate(
        count=Count(
            "userfeedback",
            filter=Q(
                userfeedback__user__stcadmin_user=user,
                userfeedback__timestamp__month=now().month,
            ),
        )
    ).order_by("-score")
    html = ["<table>"]
    for feedback_type in feedback_types:
        html.append(
            (
                f'<td><img src="{feedback_type.image.url}" alt="{feedback_type.name}" '
                f'height="15">&nbsp;{feedback_type.count}</td>'
            )
        )
    html.append("</table>")
    return mark_safe("\n".join(html))
