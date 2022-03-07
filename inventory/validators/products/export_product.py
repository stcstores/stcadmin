"""Validate the Products in a Product Export."""

from validation import BaseObjectValidator, BaseValidationCheck, Levels


class ExportProductValidationCheck(BaseValidationCheck):
    """Base validation checker for Products in a Product Export."""

    requires_matching = True

    def get_matching_model_object(self, object):
        """
        Return the matching database object for a Product.

        Return None if no database object matches the product.
        """
        return self.validation_runner.model_lookup.get(object.SKU)

    def get_test_data(self, *args, **kwargs):
        """Get required objects for testing."""
        test_data = super().get_test_data(*args, **kwargs)
        self.export_product = test_data["test_object"]
        if self.requires_matching:
            self.db_product = self.get_matching_model_object(self.export_product)
        return test_data


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
        if self.export_product is None:
            return False
        else:
            return True

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        return (
            "No Product exists in the database matching the SKU "
            f'"{self.export_product.SKU}" ("{self.export_product.name}").'
        )


class ProductNameMatchesRangeNameInDb(ExportProductValidationCheck):
    """Check an exported Products name matches it's Range name in the database."""

    name = "Product name does not match"
    level = Levels.ERROR

    def is_valid(self, *args, **kwargs):
        """Check an exported Products name matches it's Range name in the database."""
        if self.db_product is None:
            return True
        if self.db_product.product_range.name == self.export_product.name:
            return True
        else:
            return False

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        return (
            f'The name of product "{self.export_product.SKU}" '
            f'("{self.export_product.name}") does not match its range name in the '
            f'database ("{self.db_product.product_range.name}").'
        )


class LargeLetterProductIsNotLargeLetterCompatible(ExportProductValidationCheck):
    """Check that a large letter product is large letter compatible."""

    name = "Large letter product is not large letter compatible"
    level = Levels.WARNING
    requires_matching = False

    def is_valid(self, *args, **kwargs):
        """Check that a large letter product is large letter compatible."""
        large_letter_product_options = ["Large Letter", "Large Letter (Single)"]
        if self.export_product.package_type not in large_letter_product_options:
            return True
        return self.export_product.large_letter_compatible

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        return (
            f'The Product "{self.export_product.SKU}" has a large letter '
            "package type but is not large letter compatible."
        )


class ProductDescriptionMatches(ExportProductValidationCheck):
    """Check that a Products description matches in the database and Cloud Commerce."""

    name = "Product description does not match Range description"
    level = Levels.ERROR

    def is_valid(self, *args, **kwargs):
        """Check that a Products description matches in the database and Cloud Commerce."""
        if not self.db_product:
            return True
        product_description = self.clean_description(self.export_product.description)
        range_description = self.clean_description(
            self.db_product.product_range.description
        )
        return product_description == range_description

    def clean_description(self, description):
        """Remove ambiguous whitespace from the description."""
        if description is None:
            return ""
        return description.strip().replace("\n", "").replace("\t", "").replace(" ", "")

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        return (
            f'The description of product "{self.db_product.SKU}" does not match '
            f'that of Range "{self.db_product.product_range}".'
        )


class ProductFactoryMatchesSupplier(ExportProductValidationCheck):
    """Check that an exported products factory matches its supplier."""

    name = "Product factory does not match supplier"
    level = Levels.ERROR
    requires_matching = False

    def is_valid(self, *args, **kwargs):
        """Check that an exported products factory matches its supplier."""
        return self.export_product.factory == self.export_product.supplier

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        return (
            f"The factory of product {self.export_product.SKU} - "
            f'{self.export_product.name} ("{self.export_product.factory}") does not '
            f'match its supplier ("{self.export_product.supplier}").'
        )


class ProductHasCorrectHandlingTime(ExportProductValidationCheck):
    """Check that an exported product has the correct handling time."""

    name = "Product has an incorrect handling time"
    level = Levels.WARNING
    requires_matching = False

    def is_valid(self, *args, **kwargs):
        """Check that an exported product has the correct handling time."""
        return int(self.export_product.handling_time) == 1

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        return (
            f'The product "{self.export_product.SKU} - {self.export_product.name}" has '
            f'a handling time of "{self.export_product.handling_time}."'
        )


class CloudCommerceDimensionsAreNotNull(ExportProductValidationCheck):
    """Check that an exported product does not have non product option dimensions."""

    name = "Product has Cloud Commerce Dimensions"
    level = Levels.ERROR
    requires_matching = False

    def is_valid(self, *args, **kwargs):
        """Check that an exported product does not have non product option dimensions."""
        if self.export_product.cc_length != "0":
            return False
        if self.export_product.cc_width != "0":
            return False
        if self.export_product.cc_height != "0":
            return False
        return True

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        return (
            f'The product "{self.export_product.SKU} - {self.export_product.name}" has '
            "non product option dimensions."
        )


class ProductAmazonBulletPointsMatch(ExportProductValidationCheck):
    """Check a products Amazon Bullet Points match the database."""

    name = "Product Amazon Bullet Points do not match"
    level = Levels.ERROR

    def get_test_data(self, *args, **kwargs):
        """Return a list of objects to validate."""
        test_data = super().get_test_data(*args, **kwargs)
        if self.db_product is not None:
            self.export_bullets = self.export_product.amazon_bullets
            if not self.export_bullets:
                self.export_bullets = ""
            self.db_bullets = self.db_product.product_range.amazon_bullet_points
            if not self.db_bullets:
                self.db_bullets = ""
        return test_data

    def is_valid(self, *args, **kwargs):
        """Check a products Amazon Bullet Points match the database."""
        if self.db_product is None:
            return True
        return self.export_bullets == self.db_bullets

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        return (
            f'The Amazon Bullet Points of Product "{self.export_product.SKU} - '
            f'{self.export_product.name}" ("{self.export_bullets}") do not match those '
            f'of the Range in the database ("{self.db_bullets}").'
        )


class ProductAmazonSearchTermsMatch(ExportProductValidationCheck):
    """Check a products Amazon Search Terms match the database."""

    name = "Product Amazon Search Terms do not match"
    level = Levels.ERROR

    def get_test_data(self, *args, **kwargs):
        """Return a list of objects to validate."""
        test_data = super().get_test_data(*args, **kwargs)
        if self.db_product is not None:
            self.export_search_terms = self.export_product.amazon_search_terms
            if not self.export_search_terms:
                self.export_search_terms = ""
            self.db_search_terms = self.db_product.product_range.amazon_search_terms
            if not self.db_search_terms:
                self.db_search_terms = ""
        return test_data

    def is_valid(self, *args, **kwargs):
        """Check a products Amazon Bullet Points match the database."""
        if self.db_product is None:
            return True
        return self.export_search_terms == self.db_search_terms

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        return (
            f'The Amazon Search Terms of Product "{self.export_product.SKU} - '
            f'{self.export_product.name}" ("{self.export_search_terms}") do not match '
            f'those of the Range in the database ("{self.db_search_terms}").'
        )
