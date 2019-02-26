"""Validate Cloud Commerce Warehouses."""

from validation import BaseObjectValidator, BaseValidationCheck, Levels


class CCWarehouseValidationCheck(BaseValidationCheck):
    """Base validation checker for Cloud Commerce Warehouses."""

    def get_matching_model_object(self, object):
        """Return the matching database object for a warehouse.

        Return None if no database object matches the warehouse.
        """
        for model_object in self.validation_runner.model_objects:
            if model_object.warehouse_ID == object.id:
                return model_object
        return None


class CCWarehouseValidator(BaseObjectValidator):
    """Validate Cloud Commerce Warehouses."""

    name = "Cloud Commerce Warehouse"
    validation_check_class = CCWarehouseValidationCheck

    def get_test_objects(self, validation_runner):
        """Return a list of objects to validate."""
        return validation_runner.cc_warehouses


class CCWarehouseInDB(CCWarehouseValidationCheck):
    """Check a Cloud Commerce Warehouse exists in the Warehouse database model."""

    name = "Warehouse missing from Database"
    level = Levels.ERROR

    def is_valid(self, *args, **kwargs):
        """Check a Cloud Commerce Warehouse exists in the Warehouse database model."""
        model_object_IDs = [
            o.warehouse_ID for o in kwargs["validation_runner"].model_objects
        ]
        if str(kwargs["test_object"].id) not in model_object_IDs:
            return False
        else:
            return True

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        return (
            f"No Warehouse exists in the database matching the ID of "
            f'"{kwargs["test_object"].name}" ("{kwargs["test_object"].id}").'
        )
