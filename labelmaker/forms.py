from django import forms
from django.forms.models import inlineformset_factory
from labelmaker import models


class SizeChartSizeForm(forms.ModelForm):

    class Meta:
        model = models.SizeChartSize
        fields = (
            'name', 'uk_size', 'eu_size', 'us_size', 'au_size', 'sort')
        hidden_fields = ('sort', )
        widgets = {'sort': forms.HiddenInput(attrs={'class': 'size_order'})}


SizeFormset = inlineformset_factory(
    models.SizeChart, models.SizeChartSize, extra=0, form=SizeChartSizeForm)
