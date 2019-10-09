"""Save changes made in the product editor."""

import logging
import threading

from ccapi import CCAPI

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
        self.range_updater = RangeUpdater(self.original_range, self.user)
        self.range_updater.log("Begin updating.", level=logging.INFO)
        self._remove_unused_variation_options()
        self._remove_unused_listing_options()
        self._add_new_variation_options()
        self._add_new_listing_options()
        self._create_new_products()
        # Create a new range updater that recognises new products.
        self.range_updater = RangeUpdater(self.original_range, self.user)
        self._update_range_details()
        self._update_products()
        self.range_updater.log("Finish updating.", level=logging.INFO)

    def _remove_unused_variation_options(self):
        original_options = self.original_range.variation_options()
        partial_options = self.partial_range.variation_options()
        options = [_ for _ in original_options if _ not in partial_options]
        for product_option in options:
            self.range_updater.remove_product_option(product_option)

    def _remove_unused_listing_options(self):
        original_options = self.original_range.listing_options()
        partial_options = self.partial_range.listing_options()
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
            if not product.pre_existing:
                self.new_products_created = True
                self._create_product(product)

    def _create_product(self, partial_product):
        self.range_updater.log(f"Create product {partial_product}.", level=logging.INFO)
        product_ID = CCAPI.create_product(
            range_id=self.original_range.range_ID,
            name=self.original_range.name,
            description=self.original_range.description,
            barcode=partial_product.barcode,
            vat_rate=0,
            sku=partial_product.SKU,
        )
        new_product = models.Product(
            product_ID=product_ID,
            product_range=self.original_range,
            SKU=partial_product.SKU,
            supplier=partial_product.supplier,
            supplier_SKU=partial_product.supplier_SKU,
            barcode=partial_product.barcode,
            purchase_price=partial_product.purchase_price,
            VAT_rate=partial_product.VAT_rate,
            price=partial_product.price,
            retail_price=partial_product.retail_price,
            brand=partial_product.brand,
            manufacturer=partial_product.manufacturer,
            package_type=partial_product.package_type,
            international_shipping=partial_product.international_shipping,
            weight_grams=partial_product.weight_grams,
            length_mm=partial_product.length_mm,
            height_mm=partial_product.height_mm,
            width_mm=partial_product.width_mm,
            gender=partial_product.gender,
        )
        new_product.save()
        new_product.bays.set(partial_product.bays.all())
        updater = ProductUpdater(new_product, self.user)
        updater.set_date_created()
        self._update_product(partial_product, updater)

    def _update_range_details(self):
        # Set name.
        if self.partial_range.name != self.original_range.name:
            self.range_updater.set_name(self.partial_range.name)
        # Set department.
        if (
            self.new_products_created
            or self.partial_range.department != self.original_range.department
        ):
            self.range_updater.set_department(self.partial_range.department)
        # Set description.
        if self.partial_range.description != self.original_range.description:
            self.range_updater.set_description(self.partial_range.description)
        # Set amazon search terms.
        if (
            self.new_products_created
            or self.partial_range.amazon_search_terms
            != self.original_range.amazon_search_terms
        ):
            self.range_updater.set_amazon_search_terms(
                self.partial_range.amazon_search_terms
            )
        # Set amazon bullet points.
        if (
            self.new_products_created
            or self.partial_range.amazon_bullet_points
            != self.original_range.amazon_bullet_points
        ):
            self.range_updater.set_amazon_bullet_points(
                self.partial_range.amazon_bullet_points
            )

    def _update_products(self):
        for product in self.partial_range.products():
            original_product = self.original_range.product_set.get(SKU=product.SKU)
            updater = ProductUpdater(original_product, self.user)
            self._update_product(product, updater, original_product=original_product)

    def _update_product(self, partial_product, updater, original_product=None):
        self._update_product_option_links(
            partial_product, updater, original_product=original_product
        )
        # Set supplier.
        if (
            original_product is None
            or original_product.supplier != partial_product.supplier
        ):
            updater.set_supplier(partial_product.supplier)
        # Set supplier SKU.
        if (
            original_product is None
            or original_product.supplier_SKU != partial_product.supplier_SKU
        ):
            updater.set_supplier_SKU(partial_product.supplier_SKU)

        # Set Barcode.
        if (
            original_product is not None
            and original_product.barcode != partial_product.barcode
        ):  # Note: Barcode is only set for existing products as it is set at
            # product creation.
            updater.set_barcode(partial_product.barcode)
        # Set pruchase price.
        if (
            original_product is None
            or original_product.purchase_price != partial_product.purchase_price
        ):
            updater.set_purchase_price(partial_product.purchase_price)
        # Set VAT rate.
        if (
            original_product is None
            or original_product.VAT_rate != partial_product.VAT_rate
        ):
            updater.set_VAT_rate(partial_product.VAT_rate)
        # Set price.
        if original_product is None or original_product.price != partial_product.price:
            updater.set_price(partial_product.price)
        # Set retail_price.
        if (
            original_product is None
            or original_product.retail_price != partial_product.retail_price
        ):
            updater.set_retail_price(partial_product.retail_price)
        # Set brand.
        if original_product is None or original_product.brand != partial_product.brand:
            updater.set_brand(partial_product.brand)
        # Set manufacturer.
        if (
            original_product is None
            or original_product.manufacturer != partial_product.manufacturer
        ):
            updater.set_manufacturer(partial_product.manufacturer)
        # Set package type.
        if (
            original_product is None
            or original_product.package_type != partial_product.package_type
        ):
            updater.set_package_type(partial_product.package_type)
        # Set international shipping.
        if (
            original_product is None
            or original_product.international_shipping
            != partial_product.international_shipping
        ):
            updater.set_international_shipping(partial_product.international_shipping)
        # Set weight.
        if (
            original_product is None
            or original_product.weight_grams != partial_product.weight_grams
        ):
            updater.set_weight(partial_product.weight_grams)
        # Set length.
        if (
            original_product is None
            or original_product.length_mm != partial_product.length_mm
        ):
            updater.set_length(partial_product.length_mm)
        # Set height.
        if (
            original_product is None
            or original_product.height_mm != partial_product.height_mm
        ):
            updater.set_height(partial_product.height_mm)
        # Set width.
        if (
            original_product is None
            or original_product.width_mm != partial_product.width_mm
        ):
            updater.set_width(partial_product.width_mm)
        # Set gender.
        if (
            original_product is None
            or original_product.gender != partial_product.gender
        ):
            updater.set_gender(partial_product.gender)
        # Set bays.
        new_bays = list(partial_product.bays.all())
        if original_product is None or list(original_product.bays.all()) != new_bays:
            updater.set_bays(list(partial_product.bays.all()))

    def _update_product_option_links(
        self, partial_product, updater, original_product=None
    ):
        if original_product is not None:
            self._remove_old_product_option_links(
                partial_product, updater, original_product
            )
        self._add_new_product_option_links(
            partial_product, updater, original_product=original_product
        )

    def _remove_old_product_option_links(
        self, partial_product, updater, original_product
    ):
        old_links = models.ProductOptionValueLink.objects.filter(
            product=original_product
        )
        for link in old_links:
            link_exists = models.PartialProductOptionValueLink.objects.filter(
                product=partial_product, product_option_value=link.product_option_value
            )
            if not link_exists:
                updater.remove_product_option(link.product_option_value)

    def _add_new_product_option_links(
        self, partial_product, updater, original_product=None
    ):
        if original_product is None:
            return
        new_links = models.PartialProductOptionValueLink.objects.filter(
            product=partial_product
        )
        for link in new_links:
            link_exists = models.ProductOptionValueLink.objects.filter(
                product=original_product, product_option_value=link.product_option_value
            ).exists()
            if not link_exists:
                updater.set_product_option_link(link.product_option_value)
