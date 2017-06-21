from django import forms
from django.forms.utils import flatatt
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string


class ListWidget(forms.TextInput):

    list_separator = ';'

    def render(self, name, value, attrs):
        super().render(name, value, attrs)
        flat_attrs = flatatt(attrs)
        html = render_to_string(
            'cloud_commerce/list_widget.html',
            {
                'id': attrs['id'], 'attrs': flat_attrs, 'value': value,
                'name': name})
        return mark_safe(html)
