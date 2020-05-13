"""Model for fnac product translations."""

import io
from tempfile import NamedTemporaryFile

from django.contrib.postgres.fields import JSONField
from django.db import models, transaction
from openpyxl import Workbook

from fnac.tasks import start_translation_update

from .fnac_product import FnacProduct


class TranslationError(ValueError):
    """Base exception class for errors processing translations."""

    pass


class TranslationProductNotFound(TranslationError):
    """Exception raised when an imported translation has no matching product."""

    def __init__(self, product_id):
        """Raise exeption."""
        super().__init__(f"No FnacProduct matching ID {product_id} exists.")


class InvalidTranslationText(TranslationError):
    """Exception raised when translation text cannot be parsed."""

    def __init__(self):
        """Raise exeption."""
        super().__init__("Translation text could not be parsed.")


class NoTranslationsProvided(TranslationError):
    """Exception raised when translation text does not contain any translations."""

    def __init__(self):
        """Raise exeption."""
        super().__init__("No translations present in translation text.")


class TranslationHasNoDescription(TranslationError):
    """Exception raised when a translation has an empty description."""

    def __init__(self, product_id):
        """Raise exception."""
        super().__init__(
            f"No translated description found for product ID {product_id}."
        )


class TranslationManager(models.Manager):
    """Manager for the Translation model."""

    def translations_export(self):
        """Return a translation export file."""
        return _TranslationExport().translation_export()


class Translation(models.Model):
    """Model for FNAC product name, description and colour translations."""

    product = models.OneToOneField(FnacProduct, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    colour = models.CharField(max_length=255, blank=True)

    objects = TranslationManager()

    def __repr__(self):
        return f"<Translations for {self.product}>"


class TranslationUpdateManager(models.Manager):
    """Manager for the TranslationUpdate model."""

    def is_in_progress(self):
        """Return True if there is an update in progress, otherwise False."""
        return self.get_queryset().filter(status=TranslationUpdate.IN_PROGRESS).exists()

    def create_update(self, translation_text):
        """Create a translation update."""
        with transaction.atomic():
            if self.is_in_progress():
                raise TranslationUpdate.AlreadyInProgress()
            update_object = self.create(translation_text=translation_text)
            start_translation_update.delay(update_object.id)
        return update_object

    def create_invalid_upload(self, translation_text, errors):
        """Add an invalid update to the database."""
        update = self.create(
            translation_text=translation_text,
            errors=errors,
            status=TranslationUpdate.ERROR,
        )
        return update

    def update_translations(self, import_id):
        """Add translations from translation update text."""
        update_object = self.get_queryset().get(id=import_id)
        update_object.add_translations()


class TranslationUpdate(models.Model):
    """Model for translation update records."""

    class AlreadyInProgress(Exception):
        """Exception raised when an update is created with one already in progress."""

        def __init__(self, *args, **kwargs):
            """Raise the exception."""
            return super().__init__(self, "An update is already in progress.")

    COMPLETE = "complete"
    ERROR = "error"
    IN_PROGRESS = "in_progress"
    STATUSES = ((COMPLETE, "Complete"), (ERROR, "Error"), (IN_PROGRESS, "In Progress"))

    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=15, choices=STATUSES, default=IN_PROGRESS)
    translation_text = models.TextField()
    errors = JSONField(default=list)

    objects = TranslationUpdateManager()

    def add_error(self, message):
        """Mark the update with an error."""
        self.errors.append(message)
        self.status = self.ERROR
        self.save()

    def add_translations(self):
        """Create Translation objects from the translation text."""
        try:
            update_translations(self.translation_text)
        except TranslationError as e:
            self.add_error(str(e))
        except Exception as e:
            self.add_error("Error parsing translation text")
            raise e
        else:
            self.status = self.COMPLETE
            self.save()


@transaction.atomic
def update_translations(translation_text):
    """Add translations."""
    translations = _TranslationImport().get_translations(translation_text)
    for translation in translations:
        translation.save()


class _TranslationExport:
    """Translation Export File."""

    def translation_export(self):
        """Return a translation export file with currently outstanding translations."""
        workbook = Workbook()
        worksheet = workbook.active
        self.add_row(worksheet, 1, ["ID", "SKU", "Title", "Colour", "Description"])
        for i, product in enumerate(self.get_products(), 2):
            self.add_row(worksheet, i, self.product_row(product))
        return self.workbook_to_bytes(workbook)

    def get_products(self):
        return FnacProduct.objects.not_translated()

    def product_row(self, product):
        return [
            product.id,
            product.sku,
            product.name,
            product.colour or "None",
            product.description,
        ]

    def workbook_to_bytes(self, workbook):
        with NamedTemporaryFile() as tmp:
            workbook.save(tmp.name)
            tmp.seek(0)
            stream = tmp.read()
        return io.BytesIO(stream)

    def add_row(self, worksheet, row_number, row_data):
        row_data.append("¬")
        for index, column in enumerate(("A", "B", "C", "D", "E", "F")):
            worksheet[f"{column}{row_number}"] = row_data[index]


class _TranslationImport:
    """Import translations from Google Translate text."""

    def get_translations(self, translation_text):
        stripped_text = translation_text.strip().split("¬")[1:]
        if not stripped_text:
            raise NoTranslationsProvided()
        translations = [self._parse_row(row) for row in stripped_text if row]
        return translations

    def _parse_row(self, row_text):
        split = row_text.split("\t")
        product_id = self.read_sku(split[0])
        name = self.read_name(split[2])
        colour = self.read_colour(split[3])
        description = self.read_description(product_id, split[4:])
        product = self.get_product(product_id)
        return self.get_translation(
            product=product, name=name, colour=colour, description=description
        )

    def get_product(self, product_id):
        try:
            return FnacProduct.objects.get(id=product_id)
        except FnacProduct.DoesNotExist:
            raise TranslationProductNotFound(product_id)

    def get_translation(self, product, name, colour, description):
        translation, _ = Translation.objects.get_or_create(product=product)
        translation.name = name
        translation.colour = colour
        translation.description = description
        return translation

    def read_sku(self, text):
        return text.strip().replace(" ", "")

    def read_name(self, text):
        return text.strip()

    def read_colour(self, text):
        colour = text.strip()
        if colour == "Aucun":
            return ""
        return colour

    def read_description(self, product_id, lines):
        description = "".join([_.strip() for _ in lines if _])
        if description == "":
            raise TranslationHasNoDescription(product_id)
        return description
