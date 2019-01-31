"""Supplier model validators."""

from inventory import models
from validators import ModelValidator

from .factory import FactoryValidator
from .supplier_model_objects import SupplierModelObjectValidator
from .supplier_product_options import SupplierProductOptionValidator


class SupplierModelValidator(ModelValidator):
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
