"""Base models for reports."""
import csv
import io

from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import models
from file_exchange.models import FileDownload


class BaseReportDownload(FileDownload):
    """Base model for report downloads."""

    download_file = models.FileField(
        blank=True, null=True, upload_to="reports/reorder_reports"
    )
    user = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
    )
    row_count = models.PositiveIntegerField(blank=True, null=True)

    class Meta:
        """Meta class for BaseReportDownload."""

        abstract = True

    def generate_file(self):
        """Create on order export file."""
        generator_class = self._get_report_generator()
        report = generator_class(self)
        data = report.generate_csv()
        report_file = SimpleUploadedFile(
            name=self._get_filename(), content=data.encode("utf8")
        )
        self.row_count = len(report.records)
        self.save()
        return report_file


class BaseReportGenerator:
    """Base class for report generators."""

    def __init__(self, download_object):
        """Create report data."""
        self.download_object = download_object

    def get_row_kwargs(self):
        """Yield kwargs to be passed to self.make_row for each row."""
        raise NotImplementedError()

    def make_row(self, **kwargs):
        """Return a mapping of column header to value for a row in the report."""
        raise NotImplementedError()

    def _generate(self):
        self.records = [self.make_row(**kwargs) for kwargs in self.get_row_kwargs()]

    def generate_csv(self):
        """Return the export as a CSV string."""
        self._generate()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(self.header)
        for row in self.make_rows():
            writer.writerow(row)
        return output.getvalue()

    def make_rows(self, **kwargs):
        """Return the report data as a list of rows."""
        rows = []
        for record in self.records:
            row = [record.get(col, "") for col in self.header]
            rows.append(row)
        return rows
