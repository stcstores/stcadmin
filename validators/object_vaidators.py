"""Object validator base classes."""


class BaseObjectValidator:
    """Base class for object validators."""

    name = ""

    def __init__(self, validation_runner):
        """Set up validators."""
        self.error_messages = []
        self.invalid_objects = []
        self.validation_runner = validation_runner
        self.validators = [
            _(self, self.validation_runner)
            for _ in self.validation_check_class.__subclasses__()
        ]
