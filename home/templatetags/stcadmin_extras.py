"""Template tags for STCAdmin."""

from django import template
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.safestring import SafeString, mark_safe
from django.utils.timezone import now

register = template.Library()


@register.simple_tag
def tooltip(title="", text=""):
    """Return HTML for tooltip."""
    rendered_template = render_to_string(
        "home/tooltip.html", {"title": title, "text": text}
    )
    return SafeString(rendered_template)


@register.simple_tag
def user_groups(user):
    """Return a list of names of groups to which user belongs."""
    groups = user.groups.values_list("name", flat=True)
    return groups


@register.simple_tag
def tooltip_help_text(field):
    """Return rendered tooltip for a form field."""
    if field is not None and len(field.help_text) > 0:
        return tooltip(field.label, field.help_text)
    return ""


@register.simple_tag
def scayt_customer_id():
    """Return the SCAYT customer ID."""
    return settings.SCAYT_CUSTOMER_ID


@register.simple_tag
def feedback_badges(user):
    """Return rendered feedback badges."""
    from print_audit import models

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
