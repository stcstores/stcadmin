"""Base validation classes."""


class Validator:
    """Base class for validators."""

    def load_validators(self):
        """Return a list of validators."""
        return {_.name: _(self) for _ in self.validator_classes}

    def validate(self):
        """Run validation."""
        for validator in self.validators.values():
            validator.validate_all()

    @property
    def error_messages(self):
        """Return a list of error messages for all validators."""
        return sum([_.error_messages for _ in self.validators.values()], [])

    def format_error_messages(self):
        """Return a formatted string of error messages."""
        return "\n".join(self.error_messages)


class ModelValidator(Validator):
    """Base class for validating database models."""

    def __init__(self):
        """Set up validation."""
        self.model_objects = self.model.objects.all()
        self.load_cloud_commerce_data()
        self.validators = self.load_validators()

    def load_cloud_commerce_data(self):
        """Load relevent objects from Cloud Commerce."""
        raise NotImplementedError
