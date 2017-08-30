from django import template

from ccapi import URLs

from django.utils.safestring import mark_safe


register = template.Library()
SUBDOMAIN = 'seatontradingcompany'


@register.simple_tag
def ccp_product_range_page(range_id):
    return URLs.range_url(SUBDOMAIN, range_id)


@register.simple_tag
def ccp_product_page(range_id, product_id):
    return URLs.product_url(SUBDOMAIN, range_id, product_id)


@register.simple_tag
def warehouse_bays(warehouse=None):
    from ccapi import Warehouses
    if warehouse is None:
        return {x.name: x.bays for x in Warehouses}
    else:
        return Warehouses[warehouse].bays


@register.simple_tag
def product_options(option=None):
    from ccapi import ProductOptions
    if option is None:
        return {x.option_name: x.values for x in ProductOptions}
    else:
        return ProductOptions[option].options


@register.simple_tag
def feedback_badges(user):
    from print_audit import models
    try:
        user = models.CloudCommerceUser.objects.filter(
            stcadmin_user=user)[0]
    except Exception as e:
        return ''
    feedback_types = models.Feedback.objects.all()
    html = ['<table>']
    for feedback_type in feedback_types:
        count = models.UserFeedback.objects.filter(
            user=user.pk,
            feedback_type=feedback_type).count()
        html.append('<td><img src="{}" alt="{}" height="15">'.format(
            feedback_type.image.url, feedback_type.name))
        html.append('&nbsp;{}</td>'.format(count))
    html.append('</table>')
    return mark_safe('\n'.join(html))
