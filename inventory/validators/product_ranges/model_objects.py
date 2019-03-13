"""Validate inventory.ProductRange model objects."""

from validation import BaseObjectValidator, BaseValidationCheck, Levels


class ProductRangeObjectValidationCheck(BaseValidationCheck):
    """Base validation checker for ProductRange model objects."""

    def get_matching_product_range(self, model_object):
        """Return the matching product export rows for a product range model instance.

        Return None if no matching Product Range exists in the export.
        """
        return self.validation_runner.range_lookup.get(model_object.SKU)


class ProductRangeModelObjectValidator(BaseObjectValidator):
    """Validate teh ProductRange model."""

    name = "Product Range Model"
    validation_check_class = ProductRangeObjectValidationCheck

    def get_test_objects(self, validation_runner):
        """Run validation for all Product Range model objects."""
        return validation_runner.model_objects


class ProductRangeExists(ProductRangeObjectValidationCheck):
    """Check a Product Range exists in Cloud Commerce."""

    name = "Product Range missing from Cloud Commerce"
    level = Levels.ERROR

    def is_valid(self, *args, **kwargs):
        """Check a Product Range with the same Range SKU exists in Cloud Commerce."""
        if self.get_matching_product_range(kwargs["test_object"]) is None:
            return False
        else:
            return True

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        product_range = kwargs["test_object"]
        return (
            "No Product Range exists in Cloud Commerce with the Range SKU "
            f"{product_range.SKU}."
        )


class ProductRangeHasSKU(ProductRangeObjectValidationCheck):
    """Check a Product Range has a SKU."""

    name = "Product Range has no SKU"
    level = Levels.ERROR

    def is_valid(self, *args, **kwargs):
        """Check a Product Range has a SKU."""
        if not kwargs["test_object"].SKU:
            return False
        else:
            return True

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        product_range = kwargs["test_object"]
        return (
            f'The Product Range with ID "{product_range.range_ID}" has no SKU in the'
            " database."
        )


class ProductRangeHasName(ProductRangeObjectValidationCheck):
    """Check a Product Range has a name."""

    name = "Product Range has no name"
    level = Levels.ERROR

    def is_valid(self, *args, **kwargs):
        """Check a Product Range has a name."""
        if not kwargs["test_object"].name:
            return False
        else:
            return True

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        product_range = kwargs["test_object"]
        return (
            f'The Product Range with ID "{product_range.range_ID}" has no name in the'
            " database."
        )


class ProductRangeSKUContainsWhitespace(ProductRangeObjectValidationCheck):
    """Check a Product Range SKU does not contain excess whitespace."""

    name = "Product Range SKU contains whitespace"
    level = Levels.FORMATTING

    def is_valid(self, *args, **kwargs):
        """Check a Product Range SKU does not contain whitespace."""
        SKU = kwargs["test_object"].SKU
        return SKU == SKU.strip()

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        product_range = kwargs["test_object"]
        return (
            f'The SKU of the Product Range with ID "{product_range.ID}" '
            f'"{product_range.SKU}" contains whitespace."'
        )


class ProductRangeNameContainsWhitespace(ProductRangeObjectValidationCheck):
    """Check a Product Range name does not contain excess whitespace."""

    name = "Product Range name contains whitespace"
    level = Levels.FORMATTING

    def is_valid(self, *args, **kwargs):
        """Check a Product Range name does not contain whitespace."""
        name = kwargs["test_object"].name
        return name == name.strip()

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        product_range = kwargs["test_object"]
        return (
            f'The name of Product Range "{product_range.SKU}" "{product_range.name}" '
            "contains whitespace."
        )


class DBProductRangeNameMatchesProductExport(ProductRangeObjectValidationCheck):
    """Check a Product Range's name matches between the database and a Product Export."""

    name = "Product Name does not match"
    level = Levels.ERROR

    def get_test_data(self, *args, **kwargs):
        """Return dict of validation test variables."""
        test_data = super().get_test_data(*args, **kwargs)
        test_data["export_range"] = self.get_matching_product_range(
            test_data["test_object"]
        )
        return test_data

    def is_valid(self, *args, **kwargs):
        """Check a Product Range's name matches between the database and a Product Export."""
        export_range = kwargs["export_range"]
        if export_range is None:
            return True
        elif export_range.products[0].name == kwargs["test_object"].name:
            return True
        else:
            return False

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        product_range = kwargs["test_object"]
        export_range = kwargs["export_range"]
        return (
            f'The name of the Product Range with SKU "{product_range.SKU}" '
            f'("{product_range.name}") does not match the name in the Product Export: '
            f'"{export_range.products[0].name}".'
        )
