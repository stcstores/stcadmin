import json

from django import forms
from django.utils.safestring import mark_safe
from list_input import ListWidget


class HorizontalRadio(forms.RadioSelect):
    template_name = 'inventory/widgets/horizontal_radio.html'


class SelectizeWidget(forms.SelectMultiple):
    template_name = 'inventory/widgets/selectize.html'

    def __init__(self, *args, **kwargs):
        self.selectize_options = kwargs.pop('selectize_options')
        super().__init__(*args, **kwargs)

    def get_context(self, *args, **kwargs):
        context = super().get_context(*args, **kwargs)
        context['widget']['selectize_options'] = mark_safe(json.dumps(
            self.selectize_options))
        return context


class SingleSelectizeWidget(forms.Select):
    template_name = 'inventory/widgets/selectize.html'

    def __init__(self, *args, **kwargs):
        self.selectize_options = kwargs.pop('selectize_options', {})
        self.selectize_options['maxItems'] = 1
        super().__init__(*args, **kwargs)

    def get_context(self, *args, **kwargs):
        context = super().get_context(*args, **kwargs)
        context['widget']['selectize_options'] = mark_safe(json.dumps(
            self.selectize_options))
        return context


class VATPriceWidget(forms.MultiWidget):

    template_name = 'inventory/widgets/vat_price.html'
    required = True

    def __init__(self, attrs=None):
        if attrs is None:
            price_attrs = {}
        else:
            price_attrs = attrs.copy()
        price_attrs['min'] = 0
        price_attrs['step'] = 0.01
        widgets = [
            forms.Select(choices=self.vat_choices(), attrs=attrs),
            forms.NumberInput(attrs=price_attrs),
            forms.NumberInput(attrs=price_attrs)]
        super().__init__(widgets, attrs)

    @staticmethod
    def vat_choices():
        return (
            ('', ''), (20, '20%'), (5, '5%'),
            (0, 'Exempt'))

    def decompress(self, value):
        if value:
            return [value['vat_rate'], value['ex_vat'], '']
        else:
            return ['', '', '']


class DepartmentBayWidget(forms.MultiWidget):

    template_name = 'inventory/widgets/department_bay.html'
    required = False
    is_required = False

    def __init__(
            self, attrs=None, choices=[], selectize_options=[],
            lock_department=False):
        self.lock_department = lock_department
        if attrs is None:
            department_attrs = {}
            bay_attrs = {}
        else:
            department_attrs = attrs.copy()
            bay_attrs = attrs.copy()
        widgets = [
            SingleSelectizeWidget(
                attrs=department_attrs, choices=choices[0],
                selectize_options=selectize_options[0]),
            SelectizeWidget(
                attrs=bay_attrs, choices=choices[1],
                selectize_options=selectize_options[1])]
        widgets[1].is_required = False
        super().__init__(widgets, attrs)

    def decompress(self, value):
        if value:
            return [value['department'], value['bays']]
        else:
            return ['', []]

    def get_context(self, *args, **kwargs):
        context = super().get_context(*args, **kwargs)
        context['widget']['subwidgets'][1]['attrs']['required'] = False
        context['widget']['lock_department'] = self.lock_department
        return context


class OptionSettingsFieldWidget(forms.MultiWidget):

    template_name = 'inventory/widgets/options_settings_widget.html'
    required = False

    radio_choices = [
        ('unused', 'Unused'),
        ('single', 'Single'),
        ('variable', 'Variable'),
        ('variation', 'Variation')]

    def __init__(self, attrs):
        widgets = [
            HorizontalRadio(choices=self.radio_choices),
            ListWidget(),
            forms.TextInput()]
        self.required = False
        super().__init__(widgets, attrs)

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
