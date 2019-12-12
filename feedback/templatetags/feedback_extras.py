"""Template tags for the Feedback app."""
from django import template
from django.db.models import Count, Q
from django.utils.safestring import mark_safe
from django.utils.timezone import now

from print_audit import models

register = template.Library()


@register.simple_tag
def feedback_badges(user):
    """Return rendered feedback badges."""
    feedback_types = models.Feedback.objects.annotate(
        count=Count(
            "old_feedback_type",
            filter=Q(
                old_feedback_type__user__stcadmin_user=user,
                old_feedback_type__timestamp__month=now().month,
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
