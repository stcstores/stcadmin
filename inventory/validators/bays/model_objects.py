"""Validate inventory.Bay model objects."""

from validation import BaseObjectValidator, BaseValidationCheck, Levels


class BayObjectValidationCheck(BaseValidationCheck):
    """Base validation checker for Warehouse model objects."""

    pass

    def get_matching_bay(self, model_object):
        """Return the matching Cloud Commerce Bay for a Bay model instance.

        Return None if no matching warehouse exists.
        """
        for bay in self.validation_runner.cc_bays:
            if int(bay.id) == model_object.bay_id:
                return bay
        return None


class BayModelObjectValidator(BaseObjectValidator):
    """Validate the Warehouse model."""

    name = "Bay Model"
    validation_check_class = BayObjectValidationCheck

    def get_test_objects(self, validation_runner):
        """Run validation for all Bay Model Objects."""
        return validation_runner.model_objects


class BayExists(BayObjectValidationCheck):
    """Check a Cloud Commerce Bay with the same ID as the model object exists."""

    name = "Bay missing from Cloud Commerce"
    level = Levels.ERROR

    def is_valid(self, *args, **kwargs):
        """Check a Cloud Commerce Bay with the same ID as the model object exists."""
        if self.get_matching_bay(kwargs["test_object"]) is None:
            return False
        else:
            return True

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        return (
            f'No Bay with the ID of "{kwargs["test_object"]}" '
            f'("{kwargs["test_object"].bay_id}") exists in Cloud Commerce.'
        )


class BayInCorrectWarehouse(BayObjectValidationCheck):
    """Check the Bay is in the same warehouse in Cloud Commerce."""

    name = "Bay in wrong warehouse"
    level = Levels.ERROR

    def get_test_data(self, *args, **kwargs):
        """Return dict of validation test variables."""
        test_data = super().get_test_data(*args, **kwargs)
        test_data["cc_bay"] = self.get_matching_bay(test_data["test_object"])
        return test_data

    def is_valid(self, *args, **kwargs):
        """Check the Bay is in the same warehouse in the database and Cloud Commerce."""
        if kwargs["cc_bay"] is None:
            return True
        db_warehouse = kwargs["test_object"].warehouse
        cc_warehouse = kwargs["cc_bay"].warehouse
        if db_warehouse.warehouse_id != int(cc_warehouse.id):
            return False
        else:
            return True

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        bay = kwargs["test_object"]
        cc_bay = kwargs["cc_bay"]
        return (
            f'Bay "{ bay.name }" is in the warehouse "{ bay.warehouse.name }" in the'
            f' database and in "{ cc_bay.warehouse.name }" in Cloud Commerce.'
        )


class BayNameMatches(BayObjectValidationCheck):
    """Check the Bay name matches the one in Cloud Commerce."""

    name = "Bay name does not match"
    level = Levels.ERROR

    def get_test_data(self, *args, **kwargs):
        """Return dict of validation test variables."""
        test_data = super().get_test_data(*args, **kwargs)
        test_data["cc_bay"] = self.get_matching_bay(test_data["test_object"])
        return test_data

    def is_valid(self, *args, **kwargs):
        """Check the Bay ID matches the one in Cloud Commerce."""
        cc_bay = kwargs["cc_bay"]
        if kwargs["cc_bay"] is None:
            return True
        elif cc_bay.name != kwargs["test_object"].name:
            return False
        else:
            return True

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        db_bay = kwargs["test_object"]
        cc_bay = kwargs["cc_bay"]
        return (
            f'Bay "{db_bay}" does not match the Cloud Commerce name '
            f'"{cc_bay.name}" for the bay with ID '
            f'"{db_bay.bay_id}".'
        )


class NameDoesNotContainWhitespace(BayObjectValidationCheck):
    """Check the bay name does not contain whitespace."""

    name = "Name contains whitespace"
    level = Levels.FORMATTING

    def is_valid(self, *args, **kwargs):
        """Return False if the bay name contains whitespace, otherwise True."""
        return not self.contains_whitespace(kwargs["test_object"].name)

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        return f'Bay "{kwargs["test_object"]}" name cointains whitespace.'
