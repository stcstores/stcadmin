from django import forms
from list_input import ListWidget


class HorizontalRadio(forms.RadioSelect):
    template_name = 'inventory/widgets/horizontal_radio.html'


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
