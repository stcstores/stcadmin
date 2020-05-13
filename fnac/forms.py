"""Forms for the fnac app."""

from django import forms

from fnac import models


class TranslationsForm(forms.Form):
    """Form for adding translations."""

    translation_text = forms.CharField(widget=forms.Textarea())


class MiraklProductImportForm(forms.Form):
    """Form for marking products that have been created."""

    import_file = forms.FileField()

    def save(self):
        """Mark created products."""
        models.MiraklProductImport.objects.create_import(
            self.cleaned_data["import_file"]
        )


class MissingInformationUploadForm(forms.Form):
    """Form for submitting missing information updates."""

    import_file = forms.FileField()

    def save(self):
        """Import the file."""
        models.MissingInformationImport.objects.create_import(
            self.cleaned_data["import_file"]
        )
