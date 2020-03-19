"""Read a Mirakl product export and mark created products."""

import openpyxl

from .fnac_product import FnacProduct


def process_mirakl_export(export_file):
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
