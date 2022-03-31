"""Create, download and save a Cloud Commerce Pro product export."""


from pathlib import Path

from django.db import models
from tabler import Table


def export_file_path(instance, filename):
    """Return the path at which to save product export files."""
    timestamp = instance.timestamp
    filename = instance.name + ".xlsx"
    return Path("product_exports").joinpath(
        timestamp.strftime("%Y"),
        timestamp.strftime("%m"),
        timestamp.strftime("%d"),
        timestamp.strftime("%H_%M"),
        filename,
    )


class ProductExport(models.Model):
    """Model for Cloud Commerce product export files."""

    name = models.CharField(max_length=100, unique=True)
    timestamp = models.DateTimeField()
    export_file = models.FileField(upload_to=export_file_path)

    class Meta:
        """Meta class for ProductExport."""

        verbose_name = "Product Export"
        verbose_name_plural = "Product Exports"
        ordering = ("-timestamp",)

    def __str__(self):
        return f"Product Export {self.timestamp.strftime('%Y-%m-%d %H-%M')}"

    def as_table(self):
        """Return the export file as a tabler.Table instance."""
        return Table(self.export_file.path)
