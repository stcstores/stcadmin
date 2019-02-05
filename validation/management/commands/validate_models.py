"""Run validation on database models."""

import logging

from django.core.management.base import BaseCommand

from validation.run_validation import RunModelValidation

logger = logging.getLogger("management_commands")


class Command(BaseCommand):
    """Run validation on database models."""

    help = """Run validation on database models."""

    def handle(self, *args, **kwargs):
        """Run validation on database models."""
        try:
            RunModelValidation.run()
        except Exception as e:
            logger.exception("Error validating models")
            raise e
