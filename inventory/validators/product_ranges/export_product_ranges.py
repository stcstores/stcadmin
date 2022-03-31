"""Validate the Product Ranges in a Product Export."""

from validation import BaseObjectValidator, BaseValidationCheck, Levels


class ExportProductRangeValidationCheck(BaseValidationCheck):
    """Base validation checker for Product Ranges in a Product Export."""

    def get_matching_model_object(self, object):
        """Return the matching database object for a Product Range.

        Return None if no database object matches the bay.
        """
        return self.validation_runner.model_lookup.get(object.SKU)


class ExportProductRangeValidator(BaseObjectValidator):
    """Validate Product Export Product Ranges."""

    name = "Product Export Product Range"
    validation_check_class = ExportProductRangeValidationCheck

    def get_test_objects(self, validation_runner):
        """Return a list of objects to validate."""
        return validation_runner.export_ranges


class RangeInDb(ExportProductRangeValidationCheck):
    """Check an exported Product Range exists in the database."""

    name = "Product Range missing from database"
    level = Levels.ERROR

    def is_valid(self, *args, **kwargs):
        """Check an exported Product Range exists in the database."""
        if self.get_matching_model_object(kwargs["test_object"]) is None:
            return False
        else:
            return True

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        sku = kwargs["test_object"].SKU
        return f'No Product Range exists in the database matching the SKU "{sku}".'
