from django import template


register = template.Library()


@register.simple_tag
def dict_key(dictionary, *args):
    for key in args:
        dictionary = dictionary[key]
    return dictionary


@register.simple_tag
def feedback_count(user, feedback):
    return user.feedback_count(feedback)
