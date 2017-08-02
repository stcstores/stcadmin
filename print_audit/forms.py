from django import forms

from print_audit import models


class FeedbackSearchForm(forms.Form):

    PAGINATION_VALUES = [5, 10, 25, 50, 100, 250, 500, 1000, 5000]

    PAGINATION_CHOICES = [(None, '')] + [
        (int(num), str(num)) for num in PAGINATION_VALUES]

    user = forms.ModelChoiceField(
        label='User',
        required=False,
        queryset=models.CloudCommerceUser.objects.all(),
        widget=forms.RadioSelect())

    feedback = forms.ModelChoiceField(
        label='Feedback Type',
        required=False,
        queryset=models.Feedback.objects.all(),
        widget=forms.RadioSelect())

    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'datepicker'}))

    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'class': 'datepicker'}))

    paginate_by = forms.ChoiceField(
        choices=PAGINATION_CHOICES)
