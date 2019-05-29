"""Validate inventory.Product model objects."""

from validation import BaseObjectValidator, BaseValidationCheck, Levels


class ProductObjectValidationCheck(BaseValidationCheck):
    """Base validation checker for Product model objects."""

    def get_matching_product(self, model_object):
        """
        Return the matching Product Export rows for a Product model instance.

        Return None if no matching Product exists in the export.
        """
        return self.validation_runner.product_lookup.get(model_object.SKU)


class ProductModelObjectValidator(BaseObjectValidator):
    """Validate the Product model."""

    name = "Product Model"
    validation_check_class = ProductObjectValidationCheck

    def get_test_objects(self, validation_runner):
        """Run validation for all Product model objects."""
        return validation_runner.model_objects


class ProductExists(ProductObjectValidationCheck):
    """Check a Product exists in Cloud Commerce."""

    name = "Product missing from Cloud Commerce"
    level = Levels.ERROR

    def is_valid(self, *args, **kwargs):
        """Check a Product with the same SKU exists in Cloud Commerce."""
        if self.get_matching_product(kwargs["test_object"]) is None:
            return False
        else:
            return True

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        sku = kwargs["test_object"].SKU
        return f'No Product exists in Cloud Commerce with the SKU "{sku}".'
