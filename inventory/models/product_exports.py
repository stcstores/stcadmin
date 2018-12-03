"""Create, download and save a Cloud Commerce Pro product export."""

import time
from pathlib import Path

from ccapi import CCAPI


class GetProductExport:
    """Create, download and save a Cloud Commerce Pro product export."""

    def __init__(self, path=None):
        """Create, download and save a Cloud Commerce Pro product export.

        Args:
            path (pathlib.Path): The path to save the export. If it is a directory the
                export name will be used as a file name.
        """
        self.path = path
        self.existing_export_IDs = self.get_existing_export_IDs()
        self.new_export_ID = self.trigger_export()
        self.export = self.get_export_info()
        self.path = self.sanitise_path()
        CCAPI.save_product_export_file(self.export.file_name, self.path)

    def get_existing_export_IDs(self):
        """Return the IDs of all existing product exports."""
        existing_exports = CCAPI.get_product_exports().product_exports
        return [export.export_ID for export in existing_exports]

    def sanitise_path(self):
        """Return a corrected path file path for saving the export.

        If the path is None, replace it with the current working directory.
        If the path is a directory append a file name based on the product name.
        """
        path = self.path
        if path is None:
            path = Path.cwd()
        if path.is_dir():
            path = path / self.export.file_name
        return path

    def trigger_export(self):
        """Create a new product export and return it's ID."""
        CCAPI.export_products()
        exports = CCAPI.get_product_exports().product_exports
        time.sleep(5)
        new_export_ID = [
            export
            for export in exports
            if export.export_ID not in self.existing_export_IDs
        ][0].export_ID
        return new_export_ID

    def get_export_info(self):
        """Return information about the new export once available."""
        for _ in range(1000):
            export = CCAPI.get_product_exports().product_exports.get_by_ID(
                self.new_export_ID
            )
            if export.failed:
                raise Exception("Failed product export.")
            if export.complete:
                break
            time.sleep(10)
        else:
            raise Exception("Exceeded maximum attempts to retrive product export.")
        return export
