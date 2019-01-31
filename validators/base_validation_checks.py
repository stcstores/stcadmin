"""Base validation checkers."""


class BaseValidationCheck:
    """Base class for validation checks."""

    name = ""

    def __init__(self, validator, validation_runner):
        """Set the validation runner."""
        self.validator = validator
        self.validation_runner = validation_runner

    def get_test_data(self, test_object):
        """Return dict of validation test variables."""
        return {"test_object": test_object, "validation_runner": self.validation_runner}

    def validate(self, validation_object):
        """Validate an object."""
        test_data = self.get_test_data(validation_object)
        if not self.is_valid(**test_data):
            self.validator.error_messages.append(self.format_error_message(**test_data))
            self.validator.invalid_objects.append(validation_object)

    def is_valid(self, object, validation_runner):
        """Return True if the object passes the validation tests, otherwise False."""
        raise NotImplementedError()

    def format_error_message(self, test_data):
        """Return a string describing the failed validation."""
        raise NotImplementedError()
