"""Object validator base classes."""
from .levels import Levels


class BaseObjectValidator:
    """Base class for object validators."""

    name = ""

    def __init__(self, validation_runner):
        """Set up validators."""
        self.error_messages = []
        self.invalid_objects = []
        self.validation_runner = validation_runner
        self.validation_checks = [
            _ for _ in self.validation_check_class.__subclasses__()
        ]

    def get_test_objects(self, validation_runner):
        """Return a list of objects to validate."""
        raise NotImplementedError()

    def validate_all(self, level=None):
        """Run validation on all objects."""
        validation_checks = Levels.filter(self.validation_checks, level)
        for test_object in self.get_test_objects(self.validation_runner):
            for validation_check in validation_checks:
                validation_check(self, self.validation_runner, test_object)
