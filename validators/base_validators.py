"""Base validation classes."""


class ModelValidator:
    """Base class for validating database models."""

    def __init__(self):
        """Set up validation."""
        self.model_objects = self.model.objects.all()
        self.load_cloud_commerce_data()
        self.validators = self.load_validators()

    def load_cloud_commerce_data(self):
        """Load relevent objects from Cloud Commerce."""
        raise NotImplementedError

    def load_validators(self):
        """Return a list of validators."""
        raise NotImplementedError

    def validate(self):
        """Run validation."""
        raise NotImplementedError
