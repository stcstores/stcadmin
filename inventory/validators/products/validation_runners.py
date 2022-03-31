"""Product model validators."""
from inventory import models
from validation import ModelValidationRunner

from .export_product import ExportProductValidator
from .model_objects import ProductModelObjectValidator


class ProductValidationRunner(ModelValidationRunner):
    """Validator for the Product model."""

    model = models.Product
    validator_classes = [ProductModelObjectValidator, ExportProductValidator]

    def load_cloud_commerce_data(self):
        """Locad products from the most recent product export."""
        self.export = models.ProductExport.objects.latest("timestamp")
        self.export_data = self.export.export_data()
        self.export_products = self.export_data.products
        self.product_lookup = {_.SKU: _ for _ in self.export_products}
        self.model_lookup = {_.SKU: _ for _ in self.model_objects}
