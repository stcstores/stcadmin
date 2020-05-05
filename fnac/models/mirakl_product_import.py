"""Read a Mirakl product export and mark created products."""


import openpyxl
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import models, transaction
from django.utils import timezone

from fnac.tasks import start_mirakl_product_import

from .fnac_product import FnacProduct


class MiraklProductImportManager(models.Manager):
    """Manager for the MiraklProductImport model."""

    def is_in_progress(self):
        """Return True if there is an impport in progress, otherwise False."""
        return (
            self.get_queryset().filter(status=MiraklProductImport.IN_PROGRESS).exists()
        )

    def get_filename(self):
        """Return a filename for an imported file."""
        date_string = timezone.now().strftime("%Y-%m-%d")
        return f"fnac_mirakl_product_import_{date_string}.xlsx"

    def create_import(self, import_file):
        """Create a mirkal product import."""
        with transaction.atomic():
            if self.is_in_progress():
                raise MiraklProductImport.AlreadyInProgress()
            import_object = self.create(
                import_file=SimpleUploadedFile(self.get_filename(), import_file.read())
            )
            start_mirakl_product_import.delay(import_object.id)
        return import_object

    def update_products(self, import_id):
        """Update product information from a mirakl product export file."""
        import_object = self.get_queryset().get(id=import_id)
        try:
            import_mirakl_products(import_object.import_file.path)
        except Exception as e:
            import_object.status = import_object.ERROR
            import_object.save()
            raise e
        else:
            import_object.status = import_object.COMPLETE
        import_object.save()


class MiraklProductImport(models.Model):
    """Model for mirakl product import files."""

    class AlreadyInProgress(Exception):
        """Exception raised when an import is created with one already in progress."""

        def __init__(self, *args, **kwargs):
            """Raise the exception."""
            return super().__init__(self, "An import is already in progress.")

    COMPLETE = "complete"
    ERROR = "error"
    IN_PROGRESS = "in_progress"
    STATUSES = ((COMPLETE, "Complete"), (ERROR, "Error"), (IN_PROGRESS, "In Progress"))

    timestamp = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=15, choices=STATUSES, default=IN_PROGRESS)
    import_file = models.FileField(upload_to="fnac/mirakl_product_exports/", null=True)

    objects = MiraklProductImportManager()


def import_mirakl_products(export_file):
    """Read a Mirakl product export and mark created products."""
    _MarkProductsCreated().mark_created_products(export_file)


class _MarkProductsCreated:
    def mark_created_products(self, export_file):
        workbook = openpyxl.load_workbook(export_file)
        worksheet = workbook.active
        skus = self.skus(worksheet)
        FnacProduct.objects.filter(sku__in=skus).update(created=True)

    def skus(self, worksheet):
        skus = []
        for row_number, row in enumerate(worksheet.rows):
            if row_number < 2:
                continue
            skus.append(list(row)[1].value)
        return skus
