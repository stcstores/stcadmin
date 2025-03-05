"""Forms for the logs app."""

from django import forms

from logs import models


class FBALogsDateSelect(forms.Form):
    """Form for selecting log dates to views."""

    date = forms.DateField(
        widget=forms.DateInput(
            attrs={"placeholder": "Select Date", "class": "datepicker"}
        ),
    )


class WorkLogForm(forms.ModelForm):
    """Form for work logs."""

    job = forms.CharField(required=False)

    class Meta:
        """Meta class for WorkLogForm."""

        model = models.WorkLog
        fields = ("job",)
        widgets = {
            "job": forms.Textarea(attrs={"rows": 1}),
            # "date": forms.HiddenInput(),
            # "staff_member": forms.HiddenInput(),
        }


WorkLogFormset = forms.modelformset_factory(
    models.WorkLog,
    fields=["job", "date", "staff_member"],
    widgets={
        "job": forms.Textarea(attrs={"rows": 1}),
        "date": forms.HiddenInput(),
        "staff_member": forms.HiddenInput(),
    },
    extra=5,
)
