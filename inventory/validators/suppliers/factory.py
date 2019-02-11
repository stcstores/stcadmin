"""Validate Cloud Commerce Factories."""

from validation import BaseObjectValidator, BaseValidationCheck, Levels


class FactoryValidationCheck(BaseValidationCheck):
    """Base validation checker for Cloud Commerce Factories."""

    def get_matching_model_object_by_name(self, object):
        """Return the matching database object for a factory.

        Return None if no database object matches the factory.
        """
        for model_object in self.validation_runner.model_objects:
            if model_object.name == object.name:
                return model_object
        return None


class FactoryValidator(BaseObjectValidator):
    """Validate Cloud Commerce Factories."""

    name = "Factory"
    validation_check_class = FactoryValidationCheck

    def get_test_objects(self, validation_runner):
        """Return a list of objects to validate."""
        return validation_runner.factories


class FactoryInDB(FactoryValidationCheck):
    """Check a factory exists in the supplier database model."""

    name = "Factory missing from Database"
    level = Levels.ERROR

    def is_valid(self, *args, **kwargs):
        """Check a factory exists in the supplier database model."""
        model_object_names = [o.name for o in kwargs["validation_runner"].model_objects]
        if kwargs["test_object"].name not in model_object_names:
            return False
        else:
            return True

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        return f'Factory "{kwargs["test_object"]}" missing from database.'


class FactoryIDMatches(FactoryValidationCheck):
    """Check that the ID of a factory matches the factory_ID in the database."""

    name = "Factory ID does not match database."
    level = Levels.ERROR

    def get_test_data(self, *args, **kwargs):
        """Return dict of validation test variables."""
        test_data = super().get_test_data(*args, **kwargs)
        test_data["model_object"] = self.get_matching_model_object_by_name(
            test_data["test_object"]
        )
        return test_data

    def is_valid(self, *args, **kwargs):
        """Check that the ID of a factory matches the factory_ID in the database."""
        if kwargs["model_object"] is None:
            return True
        elif str(kwargs["model_object"].factory_ID) != str(kwargs["test_object"].id):
            return False
        else:
            return True

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        test_object = kwargs["test_object"]
        model_object = kwargs["model_object"]
        return (
            f'Factory "{test_object.name}" ID "{test_object.id}"'
            f' does not match database ID "{model_object.factory_ID}".'
        )
