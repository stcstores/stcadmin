"""Forms for the restock app."""

from django import forms

from inventory.models import Supplier


class UpdateSuplierOrderDateForm(forms.ModelForm):
    """Form for updating the last ordered date of a supplier."""

    class Meta:
        """Meta class for UpdateSuplierOrderDateForm."""

        model = Supplier
        fields = ("last_ordered_from",)
        widgets = {
            "last_ordered_from": forms.DateInput(
                attrs={"class": "datepicker", "size": "6"}
            )
        }
