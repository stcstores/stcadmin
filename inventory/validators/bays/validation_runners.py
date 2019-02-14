"""Bay model validators."""

from ccapi import CCAPI

from inventory import models
from validation import ModelValidationRunner

from .cc_bays import CCBayValidator
from .model_objects import BayModelObjectValidator


class BayValidationRunner(ModelValidationRunner):
    """Validator for the Bay model."""

    model = models.Bay
    validator_classes = [BayModelObjectValidator, CCBayValidator]

    def load_cloud_commerce_data(self):
        """Load relevent objects from Cloud Commerce."""
        warehouses = CCAPI.get_warehouses()
        self.cc_bays = []
        for warehouse in warehouses:
            self.cc_bays.extend(warehouse.bays)
