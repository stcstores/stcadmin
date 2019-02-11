"""Run validation checks and log error to the database."""

from . import models
from .base_validation_runners import ModelValidationRunner


class RunModelValidation:
    """Check database models are valid."""

    @classmethod
    def run(cls):
        """Check database models are valid."""
        runners = ModelValidationRunner.get_instances()
        for runner in runners:
            runner.validate()
            cls.log_runner(runner)

    @classmethod
    def log_runner(cls, runner):
        """Log errors for a validation runner."""
        models.ModelValidationLog.clear_validation_runner(runner)
        for validation_check in runner.failed_validations:
            models.ModelValidationLog.log_failed_validation(validation_check)
