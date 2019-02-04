"""Base validation classes."""
from .levels import Levels


class ValidationRunner:
    """Base class for validators."""

    validator_classes = []

    def __init__(self, level=None):
        """Create failed_validation_checks and levels."""
        self.failed_validations = []
        self.levels = {level: [] for level in Levels.levels}
        self.level = level
        self.validators = self.load_validators()

    def load_validators(self):
        """Return a list of validators."""
        return {_.name: _(self) for _ in self.validator_classes}

    def validate(self):
        """Run validation."""
        for validator in self.validators.values():
            validator.validate_all(level=self.level)
        self.failed_validations = sorted(self.failed_validations)

    def error_messages(self, level=None):
        """Return a list of error messages for all validators."""
        return [str(_) for _ in Levels.filter(self.failed_validations, level)]

    def format_error_messages(self, level=None):
        """Return a formatted string of error messages."""
        return "\n".join(self.error_messages(level=level))

    def add_failed_validation(self, validation_check):
        """Add a failed validation."""
        self.failed_validations.append(validation_check)
        if validation_check.level in self.levels:
            self.levels[validation_check.level].append(validation_check)


class ModelValidationRunner(ValidationRunner):
    """Base class for validating database models."""

    model = None

    def __init__(self, *args, **kwargs):
        """Set up validation."""
        super().__init__(*args, **kwargs)
        self.model_objects = self.model.objects.all()
        self.load_cloud_commerce_data()

    def load_cloud_commerce_data(self):
        """Load relevent objects from Cloud Commerce."""
        raise NotImplementedError
