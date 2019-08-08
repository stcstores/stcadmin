"""Save changes made in the product editor."""

import logging
import threading

from ccapi import CCAPI

from inventory import cloud_commerce_updater, models

logger = logging.getLogger("product_editor")


class SaveEdit:
    """Save changes made in the product editor."""

    def __new__(self, edit, request):
        """Make changes in a new thread."""
        self.edit = edit
        self.user = request.user
        t = threading.Thread(target=self.save_edit, args=[self])
        t.setDaemon(True)
        t.start()

    def save_edit(self):
        """Update the product."""
        self.original_range = self.edit.product_range
        self.partial_range = self.edit.partial_product_range
        self.range_updater = cloud_commerce_updater.RangeUpdater(self.original_range)
        logger.info(f"{self.user} - Range {self.original_range.SKU} - Begin update.")
        self._remove_unused_variation_options(self)
        self._remove_unused_listing_options(self)
        self._add_new_variation_options(self)
        self._add_new_listing_options(self)
        self._create_new_products(self)
        # Create a new range updater that recognises new products.
        self.range_updater = cloud_commerce_updater.RangeUpdater(self.original_range)
        self._update_range_details(self)
        self._update_products(self)
        logger.info(f"{self.user} - Range {self.original_range.SKU} - Finished update.")

    def _remove_unused_variation_options(self):
        original_options = self.original_range.variation_options()
        partial_options = self.partial_range.variation_options()
        options = [_ for _ in original_options if _ not in partial_options]
        for product_option in options:
            logger.debug(
                f'{self.user} - Range {self.original_range.SKU} - Remove variation option "{product_option}".'
            )
            self.range_updater.remove_product_option(product_option)

    def _remove_unused_listing_options(self):
        original_options = self.original_range.listing_options()
        partial_options = self.partial_range.listing_options()
        options = [_ for _ in original_options if _ not in partial_options]
        for product_option in options:
            logger.debug(
                f'{self.user} - Range {self.original_range.SKU} - Remove listing option "{product_option}".'
            )
            self.range_updater.remove_product_option(product_option)

    def _add_new_variation_options(self):
        partial_options = self.partial_range.variation_options()
        original_options = self.original_range.variation_options()
        options = [_ for _ in partial_options if _ not in original_options]
        for product_option in options:
            logger.debug(
                f'{self.user} - Range {self.original_range.SKU} - Add variation option "{product_option}".'
            )
            self.range_updater.add_variation_product_option(product_option)

    def _add_new_listing_options(self):
        partial_options = self.partial_range.listing_options()
        original_options = self.original_range.listing_options()
        options = [_ for _ in partial_options if _ not in original_options]
        for product_option in options:
            logger.debug(
                f'{self.user} - Range {self.original_range.SKU} - Add listing option "{product_option}".'
            )
            self.range_updater.add_listing_product_option(product_option)

    def _create_new_products(self):
        self.new_products_created = False
        for product in self.partial_range.products():
            if not product.pre_existing:
                self.new_products_created = True
                self._create_product(self, product)

    def _create_product(self, partial_product):
        logger.debug(
            f"{self.user} - Range {self.original_range.SKU} - Create product {partial_product}."
        )
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
        )
        new_product.save()
        new_product.bays.set(partial_product.bays.all())
        updater = cloud_commerce_updater.ProductUpdater(new_product)
        updater.set_date_created()
        self._update_product(self, partial_product, updater)

    def _update_range_details(self):
        # Set name.
        if self.partial_range.name != self.original_range.name:
            logger.debug(
                f'{self.user} - Range {self.original_range.SKU} - Set range name to "{self.partial_range.name}".'
            )
            self.range_updater.set_name(self.partial_range.name)
        # Set department.
        if (
            self.new_products_created
            or self.partial_range.department != self.original_range.department
        ):
            logger.debug(
                f'{self.user} - Range {self.original_range.SKU} - Set department to "{self.partial_range.department}".'
            )
            self.range_updater.set_department(self.partial_range.department)
        # Set description.
        if self.partial_range.description != self.original_range.description:
            logger.debug(
                f"{self.user} - Range {self.original_range.SKU} - Set description."
            )
            self.range_updater.set_description(self.partial_range.description)
        # Set amazon search terms.
        if (
            self.new_products_created
            or self.partial_range.amazon_search_terms
            != self.original_range.amazon_search_terms
        ):
            logger.debug(
                f"{self.user} - Range {self.original_range.SKU} - Set amazon search terms."
            )
            self.range_updater.set_amazon_search_terms(
                self.partial_range.amazon_search_terms
            )
        # Set amazon bullet points.
        if (
            self.new_products_created
            or self.partial_range.amazon_bullet_points
            != self.original_range.amazon_bullet_points
        ):
            logger.debug(
                f"{self.user} - Range {self.original_range.SKU} - Set amazon bullet points."
            )
            self.range_updater.set_amazon_bullet_points(
                self.partial_range.amazon_bullet_points
            )

    def _update_products(self):
        for product in self.partial_range.products():
            original_product = self.original_range.product_set.get(SKU=product.SKU)
            updater = cloud_commerce_updater.ProductUpdater(original_product)
            self._update_product(
                self, product, updater, original_product=original_product
            )

    def _update_product(self, partial_product, updater, original_product=None):
        self._update_product_option_links(
            self, partial_product, updater, original_product=original_product
        )
        # Set supplier.
        if (
            original_product is None
            or original_product.supplier != partial_product.supplier
        ):
            logger.debug(
                f'{self.user} - Product {partial_product.SKU} - Set supplier to "{partial_product.supplier}".'
            )
            updater.set_supplier(partial_product.supplier)
        # Set supplier SKU.
        if (
            original_product is None
            or original_product.supplier_SKU != partial_product.supplier_SKU
        ):
            logger.debug(
                f'{self.user} - Product {partial_product.SKU} - Set supplier SKU to "{partial_product.supplier_SKU}".'
            )
            updater.set_supplier_SKU(partial_product.supplier_SKU)

        # Set Barcode.
        if (
            original_product is not None
            and original_product.barcode != partial_product.barcode
        ):  # Note: Barcode is only set for existing products as it is set at prdouct createion.
            logger.debug(
                f'{self.user} - Product {partial_product.SKU} - Set barcode to "{partial_product.barcode}".'
            )
            updater.set_barcode(partial_product.barcode)
        # Set pruchase price.
        if (
            original_product is None
            or original_product.purchase_price != partial_product.purchase_price
        ):
            logger.debug(
                f"{self.user} - Product {partial_product.SKU} - Set purchase price to {partial_product.purchase_price}."
            )
            updater.set_purchase_price(partial_product.purchase_price)
        # Set VAT rate.
        if (
            original_product is None
            or original_product.VAT_rate != partial_product.VAT_rate
        ):
            logger.debug(
                f'{self.user} - Product {partial_product.SKU} - Set VAT rate to "{partial_product.VAT_rate}".'
            )
            updater.set_VAT_rate(partial_product.VAT_rate)
        # Set price.
        if original_product is None or original_product.price != partial_product.price:
            logger.debug(
                f"{self.user} - Product {partial_product.SKU} - Set price to {partial_product.price}."
            )
            updater.set_price(partial_product.price)
        # Set retail_price.
        if (
            original_product is None
            or original_product.retail_price != partial_product.retail_price
        ):
            logger.debug(
                f"{self.user} - Product {partial_product.SKU} - Set retail price to {partial_product.retail_price}."
            )
            updater.set_retail_price(partial_product.retail_price)
        # Set brand.
        if original_product is None or original_product.brand != partial_product.brand:
            logger.debug(
                f'{self.user} - Product {partial_product.SKU} - Set brand to "{partial_product.brand}".'
            )
            updater.set_brand(partial_product.brand)
        # Set manufacturer.
        if (
            original_product is None
            or original_product.manufacturer != partial_product.manufacturer
        ):
            logger.debug(
                f'{self.user} - Product {partial_product.SKU} - Set manufacturer to "{partial_product.manufacturer}".'
            )
            updater.set_manufacturer(partial_product.manufacturer)
        # Set package type.
        if (
            original_product is None
            or original_product.package_type != partial_product.package_type
        ):
            logger.debug(
                f'{self.user} - Product {partial_product.SKU} - Set package type to "{partial_product.package_type}".'
            )
            updater.set_package_type(partial_product.package_type)
        # Set international shipping.
        if (
            original_product is None
            or original_product.international_shipping
            != partial_product.international_shipping
        ):
            logger.debug(
                f'{self.user} - Product {partial_product.SKU} - Set international shipping to "{partial_product.international_shipping}".'
            )
            updater.set_international_shipping(partial_product.international_shipping)
        # Set weight.
        if (
            original_product is None
            or original_product.weight_grams != partial_product.weight_grams
        ):
            logger.debug(
                f"{self.user} - Product {partial_product.SKU} - Set weight to {partial_product.weight_grams}g."
            )
            updater.set_weight(partial_product.weight_grams)
        # Set length.
        if (
            original_product is None
            or original_product.length_mm != partial_product.length_mm
        ):
            logger.debug(
                f"{self.user} - Product {partial_product.SKU} - Set length to {partial_product.length_mm}mm."
            )
            updater.set_length(partial_product.length_mm)
        # Set height.
        if (
            original_product is None
            or original_product.height_mm != partial_product.height_mm
        ):
            logger.debug(
                f"{self.user} - Product {partial_product.SKU} - Set height to {partial_product.height_mm}mm."
            )
            updater.set_height(partial_product.height_mm)
        # Set width.
        if (
            original_product is None
            or original_product.width_mm != partial_product.width_mm
        ):
            logger.debug(
                f"{self.user} - Product {partial_product.SKU} - Set width to {partial_product.width_mm}mm."
            )
            updater.set_width(partial_product.width_mm)
        # Set gender.
        if (
            original_product is None
            or original_product.gender != partial_product.gender
        ):
            logger.debug(
                f'{self.user} - Product {partial_product.SKU} - Set gender to "{partial_product.gender}".'
            )
            updater.set_supplier_SKU(partial_product.gender)
        # Set bays.
        new_bays = list(partial_product.bays.all())
        if original_product is None or list(original_product.bays.all()) != new_bays:
            logger.debug(
                f"{self.user} - Product {partial_product.SKU} - Set bays to {new_bays}."
            )
            updater.set_bays(partial_product.bays.all())

    def _update_product_option_links(
        self, partial_product, updater, original_product=None
    ):
        if original_product is not None:
            self._remove_old_product_option_links(
                self, partial_product, updater, original_product
            )
        self._add_new_product_option_links(
            self, partial_product, updater, original_product=original_product
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
                logger.debug(
                    f'{self.user} - Product {original_product.SKU} - Remove product option "{link.product_option_value}".'
                )
                updater.remove_product_option(link.product_option_value)

    def _add_new_product_option_links(
        self, partial_product, updater, original_product=None
    ):
        new_links = models.PartialProductOptionValueLink.objects.filter(
            product=partial_product
        )
        for link in new_links:
            if original_product is None:
                link_exists = False
            else:
                link_exists = models.ProductOptionValueLink.objects.filter(
                    product=original_product,
                    product_option_value=link.product_option_value,
                ).exists()
            if not link_exists:
                logger.debug(
                    f'{self.user} - Product {partial_product.SKU} - Add product option "{link.product_option_value}".'
                )
                updater.set_product_option_link(link.product_option_value)
