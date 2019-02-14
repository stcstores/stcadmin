"""Warehouse model validators."""

from inventory import models
from validation import ModelValidationRunner

from .cc_warehouse import CCWarehouseValidator
from .model_objects import WarehouseModelObjectValidator


class WarehouseValidationRunner(ModelValidationRunner):
    """Validator for the Warehouse model."""

    model = models.Warehouse
    validator_classes = [WarehouseModelObjectValidator, CCWarehouseValidator]

    def load_cloud_commerce_data(self):
        """Load relevent objects from Cloud Commerce."""
        self.cc_warehouses = self.model.get_cc_warehouses()
