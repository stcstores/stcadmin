"""Update Product Ranges in the database and Cloud Commerce."""

from ccapi import CCAPI

from inventory import models

from .base_updater import BaseCloudCommerceUpdater


class RangeUpdater(BaseCloudCommerceUpdater):
    """Update a Product Range in the database and in Cloud Commerce."""

    AMAZON_SEARCH_TERMS_OPTION_ID = 41285
    AMAZON_BULLET_POINTS_OPTION_ID = 41238

    def __init__(self, db_object):
        """
        Instantiate the Range Updater.

        args:
            db_object (inventory.models.products.ProductRange)
        """
        super().__init__(db_object)
        self.product_IDs = [_.product_ID for _ in self.db_object.products()]

    def set_product_option(self, *, option_ID, value_ID):
        """Set a product option value for all of the Range's departments."""
        CCAPI.set_product_option_value(
            product_ids=self.product_IDs, option_id=option_ID, option_value_id=value_ID
        )

    def set_name(self, name: str):
        """Set the name for the Range."""
        self._set_DB_name(name)
        self._set_CC_name(name)

    def set_department(self, department):
        """
        Set the department for the Range.

        args:
            department (inventory.models.product_options.Department)
        """
        self._set_DB_department(department)
        self._set_CC_department(department)

    def set_description(self, description: str):
        """Set the description for the Range."""
        self._set_DB_description(description)
        self._set_CC_description(description)

    def set_amazon_search_terms(self, search_terms: str):
        """Set the Amazon search terms for the Range."""
        self._set_DB_amazon_search_terms(search_terms)
        self._set_CC_amazon_search_terms(search_terms)

    def set_amazon_bullet_points(self, bullet_points: str):
        """Set the Amazon search terms for the Range."""
        self._set_DB_amazon_bullet_points(bullet_points)
        self._set_CC_amazon_bullet_points(bullet_points)

    def set_end_of_line(self, end_of_line=True):
        """
        Set the Range's End-of-Line status.

        kwargs:
            end_of_line (bool): If True the Range will be set as End-of-Line, if False
                the Range will be set as not End-of-Line.
        """
        self._set_DB_end_of_line(end_of_line)
        self._set_CC_end_of_line(end_of_line)

    def add_variation_product_option(self, product_option):
        """
        Add a variation Product Option to the Range.

        args:
            product_option: inventory.models.product_options.ProductOption
        """
        self._add_DB_product_option(product_option, variation=True)
        self._add_CC_product_option(product_option, variation=True)

    def add_listing_product_option(self, product_option):
        """
        Add a listing Product Option to the Range.

        args:
            product_option: inventory.models.product_options.ProductOption
        """
        self._add_DB_product_option(product_option, variation=False)
        self._add_CC_product_option(product_option, variation=False)

    def remove_product_option(self, product_option):
        """
        Remove a Product Option from the Range.

        args:
            product_option: inventory.models.product_options.ProductOption
        """
        self._remove_DB_product_option(product_option)
        self._remove_CC_product_option(product_option)

    def _set_DB_name(self, name):
        self.db_object.name = name
        self.db_object.save()

    def _set_CC_name(self, name):
        product_range = CCAPI.get_range(self.db_object.range_ID)
        product_range.set_name(name)
        CCAPI.set_product_name(name=name, product_ids=self.product_IDs)

    def _set_DB_department(self, department):
        self.db_object.department = department
        self.db_object.save()

    def _set_CC_department(self, department):
        self.set_product_option(
            option_ID=department.PRODUCT_OPTION_ID,
            value_ID=department.product_option_value_ID,
        )

    def _set_DB_description(self, description):
        self.db_object.description = description
        self.db_object.save()

    def _set_CC_description(self, description):
        CCAPI.set_product_description(
            product_ids=self.product_IDs, description=description
        )

    def _set_DB_amazon_search_terms(self, search_terms):
        self.db_object.amazon_search_terms = search_terms
        self.db_object.save()

    def _set_CC_amazon_search_terms(self, search_terms):
        value_ID = CCAPI.get_option_value_id(
            self.AMAZON_SEARCH_TERMS_OPTION_ID, value=search_terms, create=True
        )
        self.set_product_option(
            option_ID=self.AMAZON_SEARCH_TERMS_OPTION_ID, value_ID=value_ID
        )

    def _set_DB_amazon_bullet_points(self, bullet_points):
        self.db_object.amazon_bullet_points = bullet_points
        self.db_object.save()

    def _set_CC_amazon_bullet_points(self, bullet_points):
        value_ID = CCAPI.get_option_value_id(
            self.AMAZON_BULLET_POINTS_OPTION_ID, value=bullet_points, create=True
        )
        self.set_product_option(
            option_ID=self.AMAZON_BULLET_POINTS_OPTION_ID, value_ID=value_ID
        )

    def _set_DB_end_of_line(self, end_of_line):
        self.db_object.end_of_line = bool(end_of_line)
        self.db_object.save()

    def _set_CC_end_of_line(self, end_of_line):
        product_range = CCAPI.get_range(self.db_object.range_ID)
        product_range.set_end_of_line(bool(end_of_line))

    def _add_DB_product_option(self, product_option, *, variation):
        link, created = models.ProductRangeSelectedOption.objects.get_or_create(
            product_range=self.db_object,
            product_option=product_option,
            defaults={"variation": bool(variation)},
        )
        if not created and link.variation is not bool(variation):
            link.variation = bool(variation)
            link.save()

    def _add_CC_product_option(self, product_option, *, variation):
        CCAPI.add_option_to_product(
            range_id=self.db_object.range_ID, option_id=product_option.product_option_ID
        )
        self._set_CC_product_option_variation(product_option, variation)

    def _remove_DB_product_option(self, product_option):
        models.ProductOptionValueLink.objects.filter(
            product__product_ID__in=self.product_IDs, product_option=product_option
        ).delete()
        models.ProductRangeSelectedOption.objects.get(
            product_range=self.db_object, product_option=product_option
        ).delete()

    def _remove_CC_product_option(self, product_option):
        CCAPI.remove_option_from_product(
            range_id=self.db_object.range_ID, option_id=product_option.product_option_ID
        )

    def _set_CC_product_option_variation(self, product_option, variation):
        CCAPI.set_range_option_drop_down(
            range_id=self.db_object.range_ID,
            option_id=product_option.product_option_ID,
            drop_down=variation,
        )


class PartialRangeUpdater(RangeUpdater):
    """Update a Partial Product Range in the database."""

    def set_name(self, name: str):
        """Set the name for the Range."""
        self._set_DB_name(name)

    def set_department(self, department):
        """
        Set the department for the Range.

        args:
            department (inventory.models.product_options.Department)
        """
        self._set_DB_department(department)

    def set_description(self, description: str):
        """Set the description for the Range."""
        self._set_DB_description(description)

    def set_amazon_search_terms(self, search_terms: str):
        """Set the Amazon search terms for the Range."""
        self._set_DB_amazon_search_terms(search_terms)

    def set_amazon_bullet_points(self, bullet_points: str):
        """Set the Amazon search terms for the Range."""
        self._set_DB_amazon_bullet_points(bullet_points)

    def set_end_of_line(self, end_of_line=True):
        """
        Set the Range's End-of-Line status.

        kwargs:
            end_of_line (bool): If True the Range will be set as End-of-Line, if False
                the Range will be set as not End-of-Line.
        """
        self._set_DB_end_of_line(end_of_line)

    def add_variation_product_option(self, product_option):
        """
        Add a variation Product Option to the Range.

        args:
            product_option: inventory.models.product_options.ProductOption
        """
        self._add_DB_product_option(product_option, variation=True)

    def add_listing_product_option(self, product_option):
        """
        Add a listing Product Option to the Range.

        args:
            product_option: inventory.models.product_options.ProductOption
        """
        self._add_DB_product_option(product_option, variation=False)

    def remove_product_option(self, product_option):
        """
        Remove a Product Option from the Range.

        args:
            product_option: inventory.models.product_options.ProductOption
        """
        self._remove_DB_product_option(product_option)
