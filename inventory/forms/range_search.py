from django import forms
from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string

from ccapi import CCAPI, ProductOptions


class OptionSelectField(forms.MultiValueField):

    selectable_options = (
        'WooCategory1', 'WooCategory2', 'WooCategory3', 'Manufacturer',
        'Brand', 'Supplier', 'Discontinued', 'Package Type',
        'International Shipping')
    option_choices = [('', '')]
    option_value_choices = [('', '')]
    option_matches = {}
    for option in ProductOptions:
        if option.option_name in selectable_options:
            option_choices.append((option.id, option.option_name))
            option_matches[option.id] = []
            for value in option.values:
                option_value_choices.append((value.id, value.value))
                option_matches[option.id].append(value.id)
    option_choices.sort(key=lambda x: x[1])
    option_value_choices.sort(key=lambda x: x[1])

    def __init__(self, *args, **kwargs):
        fields = (
            forms.ChoiceField(choices=self.option_choices),
            forms.ChoiceField(choices=self.option_value_choices))
        kwargs['widget'] = OptionSelectWidget(None)
        super().__init__(
            fields=fields, require_all_fields=False, *args, **kwargs)

    def compress(self, value):
        if len(value) == 0:
            return None
        return int(value[1])


class OptionSelectWidget(forms.widgets.MultiWidget):

    template_name = 'inventory/widgets/option_select_widget.html'

    def __init__(self, attrs):
        _widgets = [
            forms.Select(
                choices=OptionSelectField.option_choices),
            forms.Select(
                choices=OptionSelectField.option_value_choices)]
        super().__init__(_widgets, attrs)

    def decompress(self, value):
        if value is not None and '' not in value:
            return value
        return [None, None]

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
            self.template_name, {
                'widgets': widgets, 'name': name, 'id': id_,
                'option_matches': OptionSelectField.option_matches})
        return mark_safe(html)


class RangeSearchForm(forms.Form):

    search_type_help_text = (
        'Select a Search Type<ul><li><b>Basic Search:'
        '</b>A quick easy search which returns a limited number of items</li>'
        '<li><b>Advanced Search:</b> More options for a refined search.'
        'Will return all possible products.')

    basic_search_matches = (
        'SKU', 'Title', 'Barcode', 'Linnworks SKU', 'Linnworks Title',
        'Supplier', 'Supplier SKU', 'All Product Options')
    basic_search_help_text = 'Matches:<ul>{}</ul>'.format(
        ''.join(['<li>{}</li>'.format(text) for text in (
            basic_search_matches)]))

    advanced_search_matches = ('SKU', 'Title')
    advanced_search_help_text = 'Matches:<ul>{}</ul>'.format(
        ''.join(['<li>{}</li>'.format(text) for text in (
            advanced_search_matches)]))

    search_type = forms.ChoiceField(
        required=True,
        label='Search Type',
        help_text=search_type_help_text,
        initial='basic',
        choices=[('basic', 'Basic Search'), ('advanced', 'Advanced Search')],
        widget=forms.RadioSelect())

    hide_end_of_line = forms.BooleanField(
        required=False,
        label='Hide End of Line',
        help_text='Hide End of Line Episodes',
        initial=True)

    basic_search_text = forms.CharField(
        label='Basic Search',
        required=False,
        help_text=basic_search_help_text,
        widget=forms.TextInput(attrs={'class': 'basic_search'}))

    advanced_search_text = forms.CharField(
        label='Search Text',
        required=False,
        help_text=advanced_search_help_text,
        widget=forms.TextInput(attrs={'class': 'advanced_search'}))

    advanced_hide_out_of_stock = forms.BooleanField(
        required=False,
        label='Hide Out of Stock',
        help_text='Hide ranges with no items in stock.')

    advanced_option = OptionSelectField(
        label="Product Option", required=False,
        help_text='Search for products with a particular \
            <b>Product Option</b>')

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data['search_type'] == 'basic':
            cleaned_data = self.clean_basic_search(cleaned_data)
        elif cleaned_data['search_type'] == 'advanced':
            cleaned_data = self.clean_advanced_search(cleaned_data)
        else:
            raise ValidationError('No valid search type supplied.')
        if cleaned_data['hide_end_of_line'] is True:
            self.ranges = [r for r in self.ranges if not r.end_of_line]
        self.ranges.sort(key=lambda x: x.name)
        return cleaned_data

    def clean_basic_search(self, data):
        self.ranges = self.get_ranges(data['basic_search_text'])
        return data

    def clean_advanced_search(self, data):
        search_text = data.get('advanced_search_text')
        option_id = data.get('advanced_option', None)
        if len(search_text) == 0 and option_id == 0:
            raise ValidationError(
                'Either search text or an option must be supplied for '
                'Advanced Search')
        kwargs = {
            'search_text': search_text,
            'only_in_stock': data['advanced_hide_out_of_stock'],
            'option_matches_id': option_id,
        }
        self.ranges = CCAPI.get_ranges(**kwargs)
        return data

    def get_ranges(self, search_text):
        search_result = CCAPI.search_products(search_text)
        range_ids = list(set([result.id for result in search_result]))
        ranges = [CCAPI.get_range(range_id) for range_id in range_ids]
        return ranges
