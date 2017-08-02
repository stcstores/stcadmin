from django import template


register = template.Library()


@register.simple_tag
def feedback_count(user, feedback):
    return user.feedback_count(feedback)
