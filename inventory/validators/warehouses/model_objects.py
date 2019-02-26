"""Validate inventory.Warehouse model objects."""

from validation import BaseObjectValidator, BaseValidationCheck, Levels


class WarehouseObjectValidationCheck(BaseValidationCheck):
    """Base validation checker for Warehouse model objects."""

    pass

    def get_matching_warehouse(self, model_object):
        """Return the matching Cloud Commerce Warehouse for a Warehouse model instance.

        Return None if no matching warehouse exists.
        """
        for warehouse in self.validation_runner.cc_warehouses:
            if warehouse.id == model_object.warehouse_ID:
                return warehouse
        return None


class WarehouseModelObjectValidator(BaseObjectValidator):
    """Validate the Warehouse model."""

    name = "Warehouse Model"
    validation_check_class = WarehouseObjectValidationCheck

    def get_test_objects(self, validation_runner):
        """Run validation for all Warehouse Model Objects."""
        return validation_runner.model_objects


class WarehouseExists(WarehouseObjectValidationCheck):
    """Check a Cloud Commerce Warehouse with the same ID as the model object exists."""

    name = "Warehouse missing from Cloud Commerce"
    level = Levels.ERROR

    def is_valid(self, *args, **kwargs):
        """Check a Cloud Commerce Warehouse with the same ID as the model object exists."""
        if self.get_matching_warehouse(kwargs["test_object"]) is None:
            return False
        else:
            return True

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        return (
            f'No Warehouse with the ID of "{kwargs["test_object"].name}" '
            f'("{kwargs["test_object"].warehouse_ID}") exists in Cloud Commerce.'
        )


class WarehouseNameMatches(WarehouseObjectValidationCheck):
    """Check the Warehouse name matches the one in Cloud Commerce."""

    name = "Warehouse name does not match"
    level = Levels.ERROR

    def get_test_data(self, *args, **kwargs):
        """Return dict of validation test variables."""
        test_data = super().get_test_data(*args, **kwargs)
        test_data["cc_warehouse"] = self.get_matching_warehouse(
            test_data["test_object"]
        )
        return test_data

    def is_valid(self, *args, **kwargs):
        """Check the Warehouse ID matches the one in Cloud Commerce."""
        cc_warehouse = kwargs["cc_warehouse"]
        if kwargs["cc_warehouse"] is None:
            return True
        elif cc_warehouse.name != kwargs["test_object"].name:
            return False
        else:
            return True

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        db_warehouse = kwargs["test_object"]
        cc_warehouse = kwargs["cc_warehouse"]
        return (
            f'Database Warehouse "{db_warehouse.name}" does not match the Cloud '
            f'Commerce name "{cc_warehouse.name}" for the warehouse with ID '
            f'"{db_warehouse.warehouse_ID}".'
        )


class NameDoesNotContainWhitespace(WarehouseObjectValidationCheck):
    """Check the warehouse name does not contain whitespace."""

    name = "Name contains whitespace"
    level = Levels.FORMATTING

    def is_valid(self, *args, **kwargs):
        """Return False if the warehouse name contains whitespace, otherwise True."""
        return not self.contains_whitespace(kwargs["test_object"].name)

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        return f'Warehouse "{kwargs["test_object"]}" name cointains whitespace.'
