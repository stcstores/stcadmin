"""Save changes made in the product editor."""

import logging
import threading

from inventory import models

from .product_updater import ProductUpdater
from .range_updater import RangeUpdater

logger = logging.getLogger("product_editor")


class SaveEdit:
    """Save changes made in the product editor."""

    def __init__(self, edit, user):
        """Make changes in a new thread."""
        self.edit = edit
        self.user = user

    def save_edit_threaded(self):
        """Update the product in a new thread."""
        t = threading.Thread(target=self.save_edit, args=[])
        t.setDaemon(True)
        t.start()

    def save_edit(self):
        """Update the product."""
        self.original_range = self.edit.product_range
        self.partial_range = self.edit.partial_product_range
        if self.original_range is None:
            self.original_range = self._create_new_range()
        self.range_updater = RangeUpdater(self.original_range, self.user)
        self.range_updater.log("Begin updating.", level=logging.INFO)
        self._remove_unused_product_options()
        self._add_new_variation_options()
        self._add_new_listing_options()
        self._create_new_products()
        if self.new_products_created is True:
            self.range_updater.set_product_IDs()
        self._update_range_details()
        self._update_product_details()
        self.range_updater.log("Finish updating.", level=logging.INFO)

    def _create_new_range(self):
        return RangeUpdater.create_new_range(self.partial_range)

    def _remove_unused_product_options(self):
        original_options = self.original_range.product_options.all()
        partial_options = self.partial_range.product_options.all()
        options = [_ for _ in original_options if _ not in partial_options]
        for product_option in options:
            self.range_updater.remove_product_option(product_option)

    def _add_new_variation_options(self):
        partial_options = self.partial_range.variation_options()
        original_options = self.original_range.variation_options()
        options = [_ for _ in partial_options if _ not in original_options]
        for product_option in options:
            self.range_updater.add_variation_product_option(product_option)

    def _add_new_listing_options(self):
        partial_options = self.partial_range.listing_options()
        original_options = self.original_range.listing_options()
        options = [_ for _ in partial_options if _ not in original_options]
        for product_option in options:
            self.range_updater.add_listing_product_option(product_option)

    def _create_new_products(self):
        self.new_products_created = False
        for product in self.partial_range.products():
            if product.pre_existing is False:
                self.new_products_created = True
                self._create_product(product)

    def _create_product(self, partial_product):
        self.range_updater.log(f"Create product {partial_product}.", level=logging.INFO)
        new_product = self.range_updater.create_product(partial_product)
        updater = ProductUpdater(new_product, self.user)
        updater.set_date_created()
        _UpdateProduct(
            partial_product=partial_product,
            updater=updater,
            original_product=new_product,
            new_variation=True,
        )

    def _update_range_details(self):
        self._set_range_name()
        self._set_department()
        self._set_description()
        self._set_amazon_search_terms()
        self._set_amazon_bullet_points()

    def _update_product_details(self):
        for product in self.partial_range.products():
            original_product = self.original_range.product_set.get(SKU=product.SKU)
            updater = ProductUpdater(original_product, self.user)
            _UpdateProduct(
                partial_product=product,
                updater=updater,
                original_product=original_product,
                new_variation=False,
            )

    def _set_range_name(self):
        current_name = self.original_range.name
        new_name = self.partial_range.name
        if current_name != new_name:
            self.range_updater.set_name(new_name)

    def _set_department(self):
        current_department = self.original_range.department
        new_department = self.partial_range.department
        if self.new_products_created or new_department != current_department:
            self.range_updater.set_department(new_department)

    def _set_description(self):
        current_description = self.original_range.description
        new_description = self.partial_range.description
        if new_description != current_description:
            self.range_updater.set_description(new_description)

    def _set_amazon_search_terms(self):
        current_search_terms = self.original_range.amazon_search_terms
        new_search_terms = self.partial_range.amazon_search_terms
        if self.new_products_created or new_search_terms != current_search_terms:
            self.range_updater.set_amazon_search_terms(new_search_terms)

    def _set_amazon_bullet_points(self):
        current_bullets = self.original_range.amazon_bullet_points
        new_bullets = self.partial_range.amazon_bullet_points
        if self.new_products_created or new_bullets != current_bullets:
            self.range_updater.set_amazon_bullet_points(new_bullets)


class _UpdateProduct:
    def __init__(self, partial_product, updater, original_product, new_variation):
        self.partial_product = partial_product
        self.updater = updater
        self.original_product = original_product
        self.new_variation = new_variation
        self._update_product()

    def _update_product(self):
        self._update_product_option_links()
        self._set_supplier()
        self._set_supplier_SKU()
        self._set_barcode()
        self._set_purchase_price()
        self._set_VAT_rate()
        self._set_price()
        self._set_retail_price()
        self._set_brand()
        self._set_manufacturer()
        self._set_package_type()
        self._set_international_shipping()
        self._set_weight()
        self._set_length()
        self._set_height()
        self._set_width()
        self._set_gender()
        self._set_bays()

    def _update_product_option_links(self):
        self._remove_old_product_option_links()
        if self.new_variation is False:
            self._add_new_product_option_links()

    def _remove_old_product_option_links(self):
        old_links = models.ProductOptionValueLink.objects.filter(
            product=self.original_product
        )
        for link in old_links:
            link_exists = models.PartialProductOptionValueLink.objects.filter(
                product=self.partial_product,
                product_option_value=link.product_option_value,
            )
            if not link_exists:
                self.updater.remove_product_option_link(link.product_option_value)

    def _add_new_product_option_links(self):
        new_links = models.PartialProductOptionValueLink.objects.filter(
            product=self.partial_product
        )
        for link in new_links:
            link_exists = models.ProductOptionValueLink.objects.filter(
                product=self.original_product,
                product_option_value=link.product_option_value,
            ).exists()
            if not link_exists:
                self.updater.set_product_option_link(link.product_option_value)

    def _set_supplier(self):
        current_supplier = self.original_product.supplier
        new_supplier = self.partial_product.supplier
        if self.new_variation is True or current_supplier != new_supplier:
            self.updater.set_supplier(new_supplier)

    def _set_supplier_SKU(self):
        current_supplier_SKU = self.original_product.supplier_SKU
        new_supplier_SKU = self.partial_product.supplier_SKU
        if self.new_variation is True or current_supplier_SKU != new_supplier_SKU:
            self.updater.set_supplier_SKU(new_supplier_SKU)

    def _set_barcode(self):
        current_barcode = self.original_product.barcode
        new_barcode = self.partial_product.barcode
        if self.new_variation is False and current_barcode != new_barcode:
            self.updater.set_barcode(new_barcode)

    def _set_purchase_price(self):
        current_purchase_price = self.original_product.purchase_price
        new_purchase_price = self.partial_product.purchase_price
        if self.new_variation is True or current_purchase_price != new_purchase_price:
            self.updater.set_purchase_price(new_purchase_price)

    def _set_VAT_rate(self):
        current_VAT_rate = self.original_product.VAT_rate
        new_VAT_rate = self.partial_product.VAT_rate
        if self.new_variation is True or current_VAT_rate != new_VAT_rate:
            self.updater.set_VAT_rate(new_VAT_rate)

    def _set_price(self):
        current_price = self.original_product.price
        new_price = self.partial_product.price
        if self.new_variation is True or current_price != new_price:
            self.updater.set_price(new_price)

    def _set_retail_price(self):
        current_retail_price = self.original_product.retail_price
        new_retail_price = self.partial_product.retail_price
        if self.new_variation is True or current_retail_price != new_retail_price:
            self.updater.set_retail_price(new_retail_price)

    def _set_brand(self):
        current_barnd = self.original_product.brand
        new_brand = self.partial_product.brand
        if self.new_variation is True or current_barnd != new_brand:
            self.updater.set_brand(new_brand)

    def _set_manufacturer(self):
        current_manufacturer = self.original_product.manufacturer
        new_manufacturer = self.partial_product.manufacturer
        if self.new_variation is True or current_manufacturer != new_manufacturer:
            self.updater.set_manufacturer(new_manufacturer)

    def _set_package_type(self):
        current_product = self.original_product.package_type
        new_package_type = self.partial_product.package_type
        if self.new_variation is True or new_package_type != current_product:
            self.updater.set_package_type(new_package_type)

    def _set_international_shipping(self):
        current_international_shipping = self.original_product.international_shipping
        new_international_shipping = self.partial_product.international_shipping
        if (
            self.new_variation is True
            or current_international_shipping != new_international_shipping
        ):
            self.updater.set_international_shipping(new_international_shipping)

    def _set_weight(self):
        current_weight = self.original_product.weight_grams
        new_weight = self.partial_product.weight_grams
        if self.new_variation is True or new_weight != current_weight:
            self.updater.set_weight(new_weight)

    def _set_length(self):
        current_length = self.original_product.length_mm
        new_length = self.partial_product.length_mm
        if self.new_variation is True or new_length != current_length:
            self.updater.set_length(new_length)

    def _set_height(self):
        current_height = self.original_product.height_mm
        new_height = self.partial_product.height_mm
        if self.new_variation is True or new_height != current_height:
            self.updater.set_height(new_height)

    def _set_width(self):
        current_width = self.original_product.width_mm
        new_width = self.partial_product.width_mm
        if self.new_variation is True or new_width != current_width:
            self.updater.set_width(new_width)

    def _set_gender(self):
        current_gender = self.original_product.gender
        new_gender = self.partial_product.gender
        if self.new_variation is True or new_gender != current_gender:
            self.updater.set_gender(new_gender)

    def _set_bays(self):
        current_bays = list(self.original_product.bays.all())
        new_bays = list(self.partial_product.bays.all())
        if self.new_variation is True or new_bays != current_bays:
            self.updater.set_bays(new_bays)
