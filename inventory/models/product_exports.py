"""Create, download and save a Cloud Commerce Pro product export."""

import time
from pathlib import Path

from ccapi import CCAPI


class CCProductExport:
    """Create, download and save a Cloud Commerce Pro product export."""

    @classmethod
    def save_new_export(cls, path):
        """Create, download and save a Cloud Commerce Pro product export.

        Args:
            path (pathlib.Path): The path to save the export. If it is a directory the
                export name will be used as a file name.
        """
        export_info = cls._new_export()
        cls._save_export_file(export_info, path)

    @staticmethod
    def _get_existing_export_IDs():
        """Return the IDs of all existing product exports."""
        existing_exports = CCAPI.get_product_exports().product_exports
        return [export.export_ID for export in existing_exports]

    @staticmethod
    def _sanitise_path(path, default_file_name="Product_Export.xlsx"):
        """Return a corrected path file path for saving the export.

        If the path is None, replace it with the current working directory.
        If the path is a directory append a file name based on the product name.
        """
        if path is None:
            path = Path.cwd()
        if path.is_dir():
            path = path / default_file_name
        return path

    @staticmethod
    def _get_new_export_ID(product_exports, existing_export_IDs):
        """Return the ID of the export whos ID is not in existing_export_IDs."""
        new_export_ID = [
            export
            for export in product_exports
            if export.export_ID not in existing_export_IDs
        ][0].export_ID
        return new_export_ID

    @classmethod
    def _new_export(cls):
        """Return the export info for a newly created product export."""
        existing_export_IDs = cls._get_existing_export_IDs()
        CCAPI.export_products()
        time.sleep(5)
        product_exports = CCAPI.get_product_exports().product_exports
        export_ID = cls._get_new_export_ID(product_exports, existing_export_IDs)
        export_info = cls._get_export_info(export_ID)
        return export_info

    @classmethod
    def _save_export_file(cls, export_info, path):
        """Save a product export file."""
        path = cls._sanitise_path(path, default_file_name=export_info.file_name)
        CCAPI.save_product_export_file(export_info.file_name, path)

    @staticmethod
    def _get_export_info(export_ID):
        """Return information about the new export once available."""
        for _ in range(1000):
            export = CCAPI.get_product_exports().product_exports.get_by_ID(export_ID)
            if export.failed:
                raise Exception("Failed product export.")
            if export.complete:
                break
            time.sleep(10)
        else:
            raise Exception("Exceeded maximum attempts to retrive product export.")
        return export
