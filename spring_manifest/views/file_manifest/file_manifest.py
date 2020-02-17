"""FileManifest class."""

import logging
import sys

from spring_manifest import models

logger = logging.getLogger("file_manifest")


class FileManifest:
    """Base class for filing manifests."""

    def __init__(self, manifest):
        """File manifest."""
        self.manifest = manifest
        try:
            models.close_manifest(self.manifest)
            if self.manifest.closed is False:
                raise Exception
        except Exception as e:
            logger.error(
                "Manifest Error: %s", " ".join(sys.argv), exc_info=sys.exc_info()
            )
            self.manifest.errors = "Manifest did not close."
            raise e
        self.manifest.status = manifest.IN_PROGRESS
        self.manifest.errors = ""
        self.manifest.save()
        try:
            self.process_manifest()
        except Exception:
            self.add_error("Error processing manifest.")
            logger.error(
                "Manifest Error: %s", " ".join(sys.argv), exc_info=sys.exc_info()
            )

    def process_manifest(self):
        """Complete the manifest."""
        raise NotImplementedError

    def add_error(self, message):
        """Add error message to manifest."""
        self.manifest.status = self.manifest.FAILED
        self.manifest.errors += "{}\n".format(message)
        self.manifest.save()

    @staticmethod
    def get_order_weight(order):
        """Return weight of order in KG."""
        weight_grams = sum(
            [product.per_item_weight * product.quantity for product in order.products]
        )
        weight_kg = weight_grams / 1000
        return weight_kg

    def valid(self):
        """Return True if manifest has no errors and is not marked failed."""
        return self.manifest.status != self.manifest.FAILED and not self.manifest.errors
