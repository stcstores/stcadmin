"""Update Product Ranges in the database and Cloud Commerce."""

import logging

from ccapi import CCAPI

from inventory import models

from .base_updater import BaseCloudCommerceUpdater


class BaseRangeUpdater(BaseCloudCommerceUpdater):
    """Base updater for product ranges."""

    AMAZON_SEARCH_TERMS_OPTION_ID = 41285
    AMAZON_BULLET_POINTS_OPTION_ID = 41238

    def __init__(self, *args, **kwargs):
        """
        Instantiate the Range Updater.

        args:
            db_object (inventory.models.products.ProductRange)
        """
        super().__init__(*args, **kwargs)
        self.product_IDs = [_.product_ID for _ in self.db_object.products()]

    def set_name(self, name):
        """Set the name for the Range."""
        args, kwargs = self._prepare_set_name(name)
        if self.update_DB:
            self._set_DB_name(*args, **kwargs)
        if self.update_CC:
            self._set_CC_name(*args, **kwargs)

    def set_department(self, department):
        """
        Set the department for the Range.

        args:
            department (inventory.models.product_options.Department)
        """
        args, kwargs = self._prepare_set_department(department)
        if self.update_DB:
            self._set_DB_department(*args, **kwargs)
        if self.update_CC:
            self._set_CC_department(*args, **kwargs)

    def set_description(self, description):
        """Set the description for the Range."""
        args, kwargs = self._prepare_set_description(description)
        if self.update_DB:
            self._set_DB_description(*args, **kwargs)
        if self.update_CC:
            self._set_CC_description(*args, **kwargs)

    def set_amazon_search_terms(self, search_terms):
        """Set the Amazon search terms for the Range."""
        args, kwargs = self._prepare_set_amazon_search_terms(search_terms)
        if self.update_DB:
            self._set_DB_amazon_search_terms(*args, **kwargs)
        if self.update_CC:
            self._set_CC_amazon_search_terms(*args, **kwargs)

    def set_amazon_bullet_points(self, bullets):
        """Set the Amazon search terms for the Range."""
        args, kwargs = self._prepare_set_amazon_bullet_points(bullets)
        if self.update_DB:
            self._set_DB_amazon_bullet_points(*args, **kwargs)
        if self.update_CC:
            self._set_CC_amazon_bullet_points(*args, **kwargs)

    def set_end_of_line(self, end_of_line=True):
        """
        Set the Range's End-of-Line status.

        kwargs:
            end_of_line (bool): If True the Range will be set as End-of-Line, if False
                the Range will be set as not End-of-Line.
        """
        args, kwargs = self._prepare_set_end_of_line(end_of_line)
        if self.udpate_DB:
            self._set_DB_end_of_line(*args, **kwargs)
        if self.update_CC:
            self._set_CC_end_of_line(*args, **kwargs)

    def add_variation_product_option(self, product_option):
        """
        Add a variation Product Option to the Range.

        args:
            product_option: inventory.models.product_options.ProductOption
        """
        args, kwargs = self._prepare_add_variation_product_option(product_option)
        if self.update_DB:
            self._add_DB_product_option(*args, **kwargs)
        if self.udpate_CC:
            self._add_CC_product_option(*args, **kwargs)

    def add_listing_product_option(self, product_option):
        """
        Add a listing Product Option to the Range.

        args:
            product_option: inventory.models.product_options.ProductOption
        """
        args, kwargs = self._prepare_add_listing_product_option(product_option)
        if self.update_DB:
            self._add_DB_product_option(*args, **kwargs)
        if self.update_CC:
            self._add_CC_product_option(*args, **kwargs)

    def remove_product_option(self, product_option):
        """
        Remove a Product Option from the Range.

        args:
            product_option: inventory.models.product_options.ProductOption
        """
        args, kwargs = self._prepare_remove_product_option(product_option)
        if self.update_DB:
            self._remove_DB_product_option(*args, **kwargs)
        if self.update_CC:
            self._remove_CC_product_option(*args, **kwargs)

    def _prepare_set_name(self, name):
        self.log(f'Set name to "{name}".')
        return [name], {}

    def _prepare_set_department(self, department):
        self.log(f'Set department to "{department}".')
        return [department], {}

    def _prepare_set_description(self, description):
        self.log(f'Set description to "{description.splitlines()[0][:50]}...".')
        return [description], {}

    def _prepare_set_amazon_search_terms(self, search_terms):
        self.log(f'Set amazon search terms to "{search_terms[:50]}...".')
        return [search_terms], {}

    def _prepare_set_amazon_bullet_points(self, bullet_points):
        self.log(f'Set amazon bullet points to "{bullet_points[:50]}...".')
        return [bullet_points], {}

    def _prepare_set_end_of_line(self, end_of_line=True):
        self.log(f"Set end of line to {end_of_line}.")
        return [end_of_line], {}

    def _prepare_add_variation_product_option(self, product_option):
        self.log(f'Add variation product option "{product_option}".')
        return [product_option], {"variation": True}

    def _prepare_add_listing_product_option(self, product_option):
        self.log(f'Add listing product option "{product_option}".')
        return [product_option], {"variation": False}

    def _prepare_remove_product_option(self, product_option):
        self.log(f'Remove product option "{product_option}".')
        return [product_option], {}

    def _set_CC_product_option_value_for_products(self, *, option_ID, value_ID):
        """Set a product option value for all of the Range's departments."""
        CCAPI.set_product_option_value(
            product_ids=self.product_IDs, option_id=option_ID, option_value_id=value_ID
        )

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
        self._set_CC_product_option_value_for_products(
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
        self._set_CC_product_option_value_for_products(
            option_ID=self.AMAZON_SEARCH_TERMS_OPTION_ID, value_ID=value_ID
        )

    def _set_DB_amazon_bullet_points(self, bullet_points):
        self.db_object.amazon_bullet_points = bullet_points
        self.db_object.save()

    def _set_CC_amazon_bullet_points(self, bullet_points):
        value_ID = CCAPI.get_option_value_id(
            self.AMAZON_BULLET_POINTS_OPTION_ID, value=bullet_points, create=True
        )
        self._set_CC_product_option_value_for_products(
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
            product__product_ID__in=self.product_IDs,
            product_option_value__product_option=product_option,
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


class RangeUpdater(BaseRangeUpdater):
    """Update a Product Range in the database and in Cloud Commerce."""

    LOG_MESSAGE = "{} - Range {} - {}"
    update_DB = True
    update_CC = True


class PartialRangeUpdater(BaseRangeUpdater):
    """Update a Partial Product Range in the database."""

    LOGGING_LEVEL = logging.DEBUG
    LOG_MESSAGE = "{} - Partial Range {} - {}"
    update_DB = True
    update_CC = False
