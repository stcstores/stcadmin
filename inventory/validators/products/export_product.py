"""Validate the Products in a Product Export."""

from validation import BaseObjectValidator, BaseValidationCheck, Levels


class ExportProductValidationCheck(BaseValidationCheck):
    """Base validation checker for Products in a Product Export."""

    def get_matching_model_object(self, object):
        """
        Return the matching database object for a Product.

        Return None if no database object matches the product.
        """
        return self.validation_runner.model_lookup.get(object.SKU)


class ExportProductValidator(BaseObjectValidator):
    """Validate Product Export Products."""

    name = "Product Export Product"
    validation_check_class = ExportProductValidationCheck

    def get_test_objects(self, validation_runner):
        """Return a list of objects to validate."""
        return validation_runner.export_products


class ProductInDb(ExportProductValidationCheck):
    """Check an exported Product exists in the database."""

    name = "Product missing from database"
    level = Levels.ERROR

    def is_valid(self, *args, **kwargs):
        """Check an exported Product exists in the database."""
        if self.get_matching_model_object(kwargs["test_object"]) is None:
            return False
        else:
            return True

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        sku = kwargs["test_object"].SKU
        return f'No Product exists in the database matching the SKU "{sku}".'
