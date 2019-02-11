"""Models for the validation app."""

from django.db import models

from .levels import Levels


class ModelValidationLog(models.Model):
    """Model for failed model validations."""

    app = models.CharField(max_length=255)
    model = models.CharField(max_length=255)
    error_level = models.PositiveIntegerField()
    object_validator = models.CharField(max_length=255)
    validation_check = models.CharField(max_length=255)
    error_message = models.TextField()
    last_seen = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta class for Barcode."""

        verbose_name = "Model Validation Log"
        verbose_name_plural = "Model Validation Log"
        ordering = (
            "app",
            "model",
            "object_validator",
            "-error_level",
            "validation_check",
        )

    def __str__(self):
        return f"{self.app}.{self.model} {self.object_validator}: {self.level()}"

    def level(self):
        """Return a level object for this instances error level."""
        return Levels.get(self.error_level)

    @classmethod
    def clear_validation_runner(cls, validation_runner):
        """Delete logs for a validation runner."""
        cls._default_manager.filter(
            app=validation_runner.app_name, model=validation_runner.model_name
        ).delete()

    @classmethod
    def log_failed_validation(cls, validation_check):
        """Log a failed validation."""
        cls(
            app=validation_check.validation_runner.app_name,
            model=validation_check.validation_runner.model_name,
            error_level=validation_check.level.level,
            object_validator=validation_check.object_validator.name,
            validation_check=validation_check.name,
            error_message=validation_check.error_message,
        ).save()
