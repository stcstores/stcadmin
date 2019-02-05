"""Validate inventory.Supplier model objects."""

from validators import BaseObjectValidator, BaseValidationCheck, Levels


class SupplierObjectValidationCheck(BaseValidationCheck):
    """Base validation checker for Supplier model objects."""

    def get_matching_product_option_by_name(self, model_object):
        """Return the matching Supplier Product Option for a supplier object.

        Return None if no Product Option matches the supplier.
        """
        for option in self.validation_runner.product_options:
            if option.value == model_object.name:
                return option
        return None

    def get_matching_factory_by_name(self, model_object):
        """Return the matching Factory for a supplier object.

        Return None if no Factory matches the supplier.
        """
        for factory in self.validation_runner.factories:
            if factory.name == model_object.name:
                return factory
        return None


class SupplierModelObjectValidator(BaseObjectValidator):
    """Validate Cloud Commerce Factories."""

    name = "Supplier Model"
    validation_check_class = SupplierObjectValidationCheck

    def get_test_objects(self, validation_runner):
        """Run validation for all Supplier Model Objects."""
        return validation_runner.model_objects


class SupplierProductOptionExists(SupplierObjectValidationCheck):
    """Check a Supplier Product Option with the same name as the model object exists."""

    name = "Supplier Product Option missing from Cloud Commerce"
    level = Levels.ERROR

    def is_valid(self, *args, **kwargs):
        """Check a Supplier Product Option with the same name as the model object exists."""
        if self.get_matching_product_option_by_name(kwargs["test_object"]) is None:
            return False
        else:
            return True

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        return (
            f'Supplier Product Option "{kwargs["test_object"].name}" does not exist '
            "in Cloud Commerce."
        )


class SupplierProductOptionIDMatches(SupplierObjectValidationCheck):
    """Check the supplier option ID matches the one in Cloud Commerce."""

    name = "Supplier Product Option ID does not match"
    level = Levels.ERROR

    def get_test_data(self, *args, **kwargs):
        """Return dict of validation test variables."""
        test_data = super().get_test_data(*args, **kwargs)
        test_data["product_option"] = self.get_matching_product_option_by_name(
            test_data["test_object"]
        )
        return test_data

    def is_valid(self, *args, **kwargs):
        """Check the supplier option ID matches the one in Cloud Commerce."""
        product_option = kwargs["product_option"]
        if kwargs["product_option"] is None:
            return True
        elif str(product_option.id) != kwargs["test_object"].product_option_ID:
            return False
        else:
            return True

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        product_option = kwargs["product_option"]
        return (
            f'Supplier Product Option "{product_option.value}"\'s ID '
            f'"{product_option.id}" does not match database value '
            f'"{kwargs["test_object"].product_option_ID}".'
        )


class FactoryExists(SupplierObjectValidationCheck):
    """Check a Factory with the same name as the model object exists."""

    name = "Factory missing from Cloud Commerce"
    level = Levels.ERROR

    def is_valid(self, *args, **kwargs):
        """Check a Factory with the same name as the model object exists."""
        if self.get_matching_factory_by_name(kwargs["test_object"]) is None:
            return False
        else:
            return True

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        return f'Factory "{kwargs["test_object"]}" does not exist in Cloud Commerce.'


class FactoryIDMatches(SupplierObjectValidationCheck):
    """Check the Factory ID matches the one in Cloud Commerce."""

    name = "Factory ID does not match"
    level = Levels.ERROR

    def get_test_data(self, *args, **kwargs):
        """Return dict of validation test variables."""
        test_data = super().get_test_data(*args, **kwargs)
        test_data["factory"] = self.get_matching_factory_by_name(
            test_data["test_object"]
        )
        return test_data

    def is_valid(self, *args, **kwargs):
        """Check the supplier option ID matches the one in Cloud Commerce."""
        if kwargs["factory"] is None:
            return True
        elif str(kwargs["factory"].id) != kwargs["test_object"].factory_ID:
            return False
        else:
            return True

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        factory = kwargs["factory"]
        return (
            f'Factory "{factory.name}"\'s ID "{factory.id}" does not '
            f'match database value "{kwargs["test_object"].factory_ID}".'
        )


class NameDoesNotContainWhitespace(SupplierObjectValidationCheck):
    """Check the supplier name does not contain whitespace."""

    name = "Name contains whitespace"
    level = Levels.FORMATTING

    def is_valid(self, *args, **kwargs):
        """Return False if the supplier name contains whitespace, otherwise True."""
        return not self.contains_whitespace(kwargs["test_object"].name)

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        return f'Supplier "{kwargs["test_object"]}" name cointains whitespace.'
