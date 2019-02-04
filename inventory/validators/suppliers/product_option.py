"""Validate the Cloud Commerce Supplier Product Options."""

from validators import BaseObjectValidator, BaseValidationCheck, Levels


class SupplierProductOptionValidationCheck(BaseValidationCheck):
    """Base validation check for the Supplier Product Options."""

    def validate_all(self):
        """Validate all Supplier Product Options."""
        for product_option in self.validation_runner.product_options:
            self.validate(product_option)

    def get_matching_model_object_by_name(self, test_object):
        """Return the matching database object for a Suppler Product Option.

        Return None if no database object matches the Supplier Product Option.
        """
        for model_object in self.validation_runner.model_objects:
            if model_object.name == test_object.value:
                return model_object
        return None


class SupplierProductOptionValidator(BaseObjectValidator):
    """Validate the Cloud Commerce Supplier Product Options."""

    name = "supplier_product_options"
    validation_check_class = SupplierProductOptionValidationCheck

    def get_test_objects(self, validation_runner):
        """Return a list of objects to validate."""
        return validation_runner.product_options


class SupplierProductOptionInDB(SupplierProductOptionValidationCheck):
    """Check a Supplier Product Option exists the the Supplier database model."""

    name = "Supplier Product Option Missing From Database"
    level = Levels.ERROR

    def is_valid(self, *args, **kwargs):
        """Check a Supplier Product Option exists the the Supplier database model."""
        model_names = [_.name for _ in kwargs["validation_runner"].model_objects]
        if kwargs["test_object"].value not in model_names:
            return False
        else:
            return True

    def format_error_message(*args, **kwargs):
        """Return a string describing the failed validation."""
        return f'Supplier Product Option "{kwargs["test_object"].value}" missing from database.'


class SupplierProductOptionIDMatches(SupplierProductOptionValidationCheck):
    """Check a Supplier Product Option's ID matches the Supplier database model."""

    name = "Supplier Product Option ID does not match database."
    level = Levels.ERROR

    def get_test_data(self, *args, **kwargs):
        """Return dict of validation test variables."""
        test_data = super().get_test_data(*args, **kwargs)
        test_data["model_object"] = self.get_matching_model_object_by_name(
            test_data["test_object"]
        )
        return test_data

    def is_valid(self, *args, **kwargs):
        """Check a Supplier Product Option's ID matches the Supplier database model."""
        model_object = kwargs["model_object"]
        if model_object is None:
            return True
        if str(model_object.product_option_ID) != str(kwargs["test_object"].id):
            return False
        else:
            return True

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        test_object = kwargs["test_object"]
        model_object = kwargs["model_object"]
        return (
            f'Supplier "{test_object.value}" Product Option ID "{test_object.id}"'
            f' does not match database ID "{model_object.product_option_ID}".'
        )
