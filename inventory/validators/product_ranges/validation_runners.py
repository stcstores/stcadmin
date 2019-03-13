"""Product Range model validators."""
from inventory import models
from validation import ModelValidationRunner

from .export_product_ranges import ExportProductRangeValidator
from .model_objects import ProductRangeModelObjectValidator


class ProductRangeValidationRunner(ModelValidationRunner):
    """Validator for the ProductRange model."""

    model = models.ProductRange
    validator_classes = [ProductRangeModelObjectValidator, ExportProductRangeValidator]

    def load_cloud_commerce_data(self):
        """Load ranges from the most recent product export."""
        self.export = models.ProductExport.objects.latest("timestamp")
        self.export_data = self.export.export_data()
        self.export_ranges = self.export_data.ranges
        self.range_lookup = {_.SKU: _ for _ in self.export_ranges}
        self.model_lookup = {_.SKU: _ for _ in self.model_objects}
