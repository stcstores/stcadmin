"""Supplier model validators."""

from inventory import models
from validation import ModelValidationRunner

from .factory import FactoryValidator
from .model_objects import SupplierModelObjectValidator
from .product_option import SupplierProductOptionValidator


class SupplierValidationRunner(ModelValidationRunner):
    """Validator for the Supplier model."""

    model = models.Supplier
    validator_classes = [
        SupplierProductOptionValidator,
        FactoryValidator,
        SupplierModelObjectValidator,
    ]

    def load_cloud_commerce_data(self):
        """Load relevent objects from Cloud Commerce."""
        self.factories = self.model.get_factories()
        self.product_options = self.model.get_supplier_product_options()
