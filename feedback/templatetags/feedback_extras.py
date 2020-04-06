"""Template tags for the Feedback app."""
from django import template
from django.db.models import Count, Q
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
    return feedback_types
