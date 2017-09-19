from django import template
from django.template.loader import render_to_string
from django.utils.safestring import SafeString
from stcadmin import settings

register = template.Library()


@register.simple_tag
def tooltip(title='', text=''):
    rendered_template = render_to_string(
        'home/tooltip.html', {'title': title, 'text': text})
    return SafeString(rendered_template)


@register.simple_tag
def tooltip_help_text(field):
    if field is not None and len(field) > 0:
        return tooltip(field.label, field.help_text)
    return None


@register.simple_tag
def scayt_customer_id():
    return settings.SCAYT_CUSTOMER_ID
