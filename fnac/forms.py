"""Forms for the fnac app."""

from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction

from fnac import models


class TranslationsForm(forms.Form):
    """Form for adding translations."""

    translations = forms.CharField(widget=forms.Textarea())

    def clean_translations(self):
        """Prevent empty form submissions."""
        text = self.cleaned_data.get("translations")
        try:
            translations = models.Translation.objects.translations_from_text(text)
        except models.Translation.TranslationProductNotFound as e:
            raise ValidationError(str(e))
        except Exception as e:
            raise ValidationError(f"Error parsing translation text: {e}.")
        if len(translations) == 0:
            raise ValidationError("No translations found.")
        return translations

    @transaction.atomic
    def save(self):
        """Save the translations."""
        for translation in self.cleaned_data["translations"]:
            translation.save()


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
