"""Widgets for custom or combined fields."""

import json

from django import forms
from django.utils.safestring import mark_safe


class HorizontalRadio(forms.RadioSelect):
    """Widget for radio buttons layed out horizontally."""

    template_name = 'inventory/widgets/horizontal_radio.html'


class BaseSelectizeWidget:
    """Base class for widgets using selectize.js."""

    template_name = 'inventory/widgets/selectize.html'


class MultipleSelectizeWidget(BaseSelectizeWidget, forms.SelectMultiple):
    """Widget for selectize fields allowing multiple values."""

    def __init__(self, *args, **kwargs):
        """Set selectize options."""
        self.selectize_options = kwargs.pop('selectize_options')
        super().__init__(*args, **kwargs)

    def get_context(self, *args, **kwargs):
        """Return context for template."""
        context = super().get_context(*args, **kwargs)
        context['widget']['selectize_options'] = mark_safe(json.dumps(
            self.selectize_options))
        return context


class SingleSelectizeWidget(BaseSelectizeWidget, forms.Select):
    """Widget for selectize fields allowing a single value."""

    def __init__(self, *args, **kwargs):
        """Set selectize options."""
        self.selectize_options = kwargs.pop('selectize_options', {})
        self.selectize_options['maxItems'] = 1
        super().__init__(*args, **kwargs)

    def get_context(self, *args, **kwargs):
        """Return context for template."""
        context = super().get_context(*args, **kwargs)
        context['widget']['selectize_options'] = mark_safe(json.dumps(
            self.selectize_options))
        return context


class VATPriceWidget(forms.MultiWidget):
    """Widget for VATPrice field."""

    template_name = 'inventory/widgets/vat_price.html'
    required = True

    def __init__(self, attrs=None):
        """Configure sub widgets."""
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
        """Return choices."""
        return (
            ('', ''), (20, '20%'), (5, '5%'),
            (0, 'Exempt'))

    def decompress(self, value):
        """Return value as a list of values."""
        if value:
            return [value['vat_rate'], value['ex_vat'], '']
        else:
            return ['', '', '']


class DepartmentBayWidget(forms.MultiWidget):
    """Widget for DepartmentBay field."""

    template_name = 'inventory/widgets/department_bay.html'
    required = False
    is_required = False

    def __init__(
            self, attrs=None, choices=[], selectize_options=[],
            lock_department=False):
        """Configure sub widgets."""
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
            MultipleSelectizeWidget(
                attrs=bay_attrs, choices=choices[1],
                selectize_options=selectize_options[1])]
        widgets[1].is_required = False
        super().__init__(widgets, attrs)

    def decompress(self, value):
        """Return value as a list of values."""
        if value:
            return [value['department'], value['bays']]
        else:
            return ['', []]

    def get_context(self, *args, **kwargs):
        """Return context for template."""
        context = super().get_context(*args, **kwargs)
        context['widget']['subwidgets'][1]['attrs']['required'] = False
        context['widget']['lock_department'] = self.lock_department
        return context


class DimensionsWidget(forms.MultiWidget):
    """Widget for Dimensions field."""

    template_name = 'inventory/widgets/dimensions.html'
    required = False
    is_required = False

    def __init__(self, *args, **kwargs):
        """Configure sub widgets."""
        attrs = kwargs.get('attrs', None)
        widgets = [
            forms.NumberInput(attrs=attrs), forms.NumberInput(attrs=attrs),
            forms.NumberInput(attrs=attrs)]
        super().__init__(widgets, attrs)

    def decompress(self, value):
        """Return value as a list of values."""
        if value:
            return [value['height'], value['length'], value['width']]
        else:
            return ['', '', '']
