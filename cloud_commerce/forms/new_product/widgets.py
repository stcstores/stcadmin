from django import forms
from django.forms.utils import flatatt
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string


class ListWidget(forms.TextInput):

    list_separator = ';'

    def render(self, name, value, attrs):
        flat_attrs = flatatt(attrs)
        html = render_to_string(
            'cloud_commerce/list_widget.html',
            {
                'id': attrs['id'], 'attrs': flat_attrs, 'value': value,
                'name': name})
        return mark_safe(html)


class HorizontalRadioRenderer(forms.RadioSelect.renderer):
    def render(self):
        return mark_safe(u'\n'.join([u'%s\n' % w for w in self]))


class OptionSettingsFieldWidget(forms.MultiWidget):

    template_name = 'cloud_commerce/options_settings_widget.html'

    radio_choices = [
        ('unused', 'Unused'),
        ('single', 'Single'),
        ('variable', 'Variable'),
        ('variation', 'Variation')]

    def __init__(self, attrs):
        _widgets = [
            forms.RadioSelect(
                choices=self.radio_choices, renderer=HorizontalRadioRenderer),
            ListWidget(),
            forms.TextInput()]
        super().__init__(_widgets, attrs)

    def decompress(self, value):
        if value:
            use = value[0]
            li = value[1]
            text = value[2]
            if use == 'unused':
                return [use, [], '']
            if use == 'single' or use == 'variable':
                return [use, [], text]
            if use == 'variation':
                return [use, li, '']
        return [None, None, None]

    def render(self, name, value, attrs=None):
        values = self.decompress(value)
        final_attrs = self.build_attrs(attrs)
        final_attrs['required'] = False
        id_ = final_attrs.get('id')
        widgets = []
        for i, widget in enumerate(self.widgets):
            widget_attrs = dict(final_attrs, id='%s_%s' % (id_, i))
            widget_name = name + '_%s' % i
            rendered_widget = widget.render(
                widget_name, values[i], widget_attrs)
            widgets.append(rendered_widget)
        html = render_to_string(
            'cloud_commerce/options_settings_widget.html',
            {'widgets': widgets, 'name': name, 'id': id_})
        return mark_safe(html)
