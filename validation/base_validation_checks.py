"""Base validation checkers."""


class BaseValidationCheck:
    """Base class for validation checks."""

    abstract = False
    name = ""
    level = None

    def __init__(self, object_validator, validation_runner, validation_object):
        """Set the validation runner."""
        self.validation_runner = validation_runner
        self.object_validator = object_validator
        self.validation_object = validation_object
        self.error_message = ""
        self.validate(validation_object)

    def __repr__(self):
        return f"Validation Check: {self.name}"

    def __str__(self):
        return f"{self.level}: {self.error_message}"

    def __lt__(self, other):
        return self.level > other.level

    def get_test_data(self, test_object):
        """Return dict of validation test variables."""
        return {"test_object": test_object, "validation_runner": self.validation_runner}

    def validate(self, validation_object):
        """Validate an object."""
        self.validation_object = validation_object
        test_data = self.get_test_data(self.validation_object)
        if not self.is_valid(**test_data):
            self.error_message = self.format_error_message(**test_data)
            self.validation_runner.add_failed_validation(self)

    def is_valid(self, *args, **kwargs):
        """Return True if the object passes the validation tests, otherwise False."""
        raise NotImplementedError()

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        raise NotImplementedError()

    def contains_whitespace(self, text):
        """Return True if text contains whitespace, otherwise return False."""
        return str(text) != str(text).strip()
