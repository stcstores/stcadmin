"""Save changes made in the product editor."""
import logging
import threading

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
        for product in self.partial_range.products():
            if not product.product_ID:
                self._create_product(self, product)

    def _create_product(self, product):
        logger.debug(
            f"{self.user} - Range {self.original_range.SKU} - Create product {product}."
        )
        raise NotImplementedError

    def _update_range_details(self):
        if self.partial_range.name != self.original_range.name:
            logger.debug(
                f'{self.user} - Range {self.original_range.SKU} - Set range name to "{self.partial_range.name}".'
            )
            self.range_updater.set_name(self.partial_range.name)
        if self.partial_range.department != self.original_range.department:
            logger.debug(
                f'{self.user} - Range {self.original_range.SKU} - Set department to "{self.partial_range.department}".'
            )
            self.range_updater.set_department(self.partial_range.department)
        if self.partial_range.description != self.original_range.description:
            logger.debug(
                f"{self.user} - Range {self.original_range.SKU} - Set description."
            )
            self.range_updater.set_description(self.partial_range.description)
        if (
            self.partial_range.amazon_search_terms
            != self.original_range.amazon_search_terms
        ):
            logger.debug(
                f"{self.user} - Range {self.original_range.SKU} - Set amazon search terms."
            )
            self.range_updater.set_amazon_search_terms(
                self.partial_range.amazon_search_terms
            )
        if (
            self.partial_range.amazon_bullet_points
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
            self._update_product(self, product)

    def _update_product(self, partial_product):
        original_product = self.original_range.product_set.get(SKU=partial_product.SKU)
        updater = cloud_commerce_updater.ProductUpdater(original_product)
        self._update_product_option_links(
            self, partial_product, original_product, updater
        )
        if original_product.supplier != partial_product.supplier:
            logger.debug(
                f'{self.user} - Product {original_product.SKU} - Set supplier to "{partial_product.supplier}".'
            )
            updater.set_supplier(partial_product.supplier)
        if original_product.supplier_SKU != partial_product.supplier_SKU:
            logger.debug(
                f'{self.user} - Product {original_product.SKU} - Set supplier SKU to "{partial_product.supplier_SKU}".'
            )
            updater.set_supplier_SKU(partial_product.supplier_SKU)
        if original_product.barcode != partial_product.barcode:
            logger.debug(
                f'{self.user} - Product {original_product.SKU} - Set barcode to "{self.partial_product.barcode}".'
            )
            updater.set_barcode(partial_product.barcode)
        if original_product.purchase_price != partial_product.purchase_price:
            logger.debug(
                f"{self.user} - Product {original_product.SKU} - Set purchase price to {partial_product.purchase_price}."
            )
            updater.set_purchase_price(partial_product.purchase_price)
        if original_product.VAT_rate != partial_product.VAT_rate:
            logger.debug(
                f'{self.user} - Product {original_product.SKU} - Set VAT rate to "{partial_product.VAT_rate}".'
            )
            updater.set_VAT_rate(partial_product.VAT_rate)
        if original_product.price != partial_product.price:
            logger.debug(
                f"{self.user} - Product {original_product.SKU} - Set price to {partial_product.price}."
            )
            updater.set_price(partial_product.price)
        if original_product.retail_price != partial_product.retail_price:
            logger.debug(
                f"{self.user} - Product {original_product.SKU} - Set retail price to {partial_product.retail_price}."
            )
            updater.set_retail_price(partial_product.retail_price)
        if original_product.brand != partial_product.brand:
            logger.debug(
                f'{self.user} - Product {original_product.SKU} - Set brand to "{partial_product.brand}".'
            )
            updater.set_brand(partial_product.brand)
        if original_product.manufacturer != partial_product.manufacturer:
            logger.debug(
                f'{self.user} - Product {original_product.SKU} - Set manufacturer to "{partial_product.manufacturer}".'
            )
            updater.set_manufacturer(partial_product.manufacturer)
        if original_product.package_type != partial_product.package_type:
            logger.debug(
                f'{self.user} - Product {original_product.SKU} - Set package type to "{partial_product.package_type}".'
            )
            updater.set_package_type(partial_product.package_type)
        if (
            original_product.international_shipping
            != partial_product.international_shipping
        ):
            logger.debug(
                f'{self.user} - Product {original_product.SKU} - Set international shipping to "{partial_product.international_shipping}".'
            )
            updater.set_international_shipping(partial_product.international_shipping)
        if original_product.weight_grams != partial_product.weight_grams:
            logger.debug(
                f"{self.user} - Product {original_product.SKU} - Set weight to {partial_product.weight}g."
            )
            updater.set_weight(partial_product.weight_grams)
        if original_product.length_mm != partial_product.length_mm:
            logger.debug(
                f"{self.user} - Product {original_product.SKU} - Set length to {partial_product.length_mm}mm."
            )
            updater.set_length(partial_product.length_mm)
        if original_product.height_mm != partial_product.height_mm:
            logger.debug(
                f"{self.user} - Product {original_product.SKU} - Set height to {partial_product.height_mm}mm."
            )
            updater.set_height(partial_product.height_mm)
        if original_product.width_mm != partial_product.width_mm:
            logger.debug(
                f"{self.user} - Product {original_product.SKU} - Set width to {partial_product.width_mm}mm."
            )
            updater.set_width(partial_product.width_mm)
        if original_product.gender != partial_product.gender:
            logger.debug(f'{self.user} - Set gender to "{partial_product.gender}".')
            updater.set_supplier_SKU(partial_product.gender)
        new_bays = list(partial_product.bays.all())
        if list(original_product.bays.all()) != new_bays:
            logger.debug(
                f"{self.user} - Product {original_product.SKU} - Set bays to {new_bays}."
            )
            updater.set_bays(partial_product.bays.all())

    def _update_product_option_links(self, partial_product, original_product, updater):
        self._remove_old_product_option_links(
            self, partial_product, original_product, updater
        )
        self._add_new_product_option_links(
            self, partial_product, original_product, updater
        )

    def _remove_old_product_option_links(
        self, partial_product, original_product, updater
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

    def _add_new_product_option_links(self, partial_product, original_product, updater):
        new_links = models.PartialProductOptionValueLink.objects.filter(
            product=partial_product
        )
        for link in new_links:
            link_exists = models.ProductOptionValueLink.objects.filter(
                product=original_product, product_option_value=link.product_option_value
            ).exists()
            if not link_exists:
                logger.debug(
                    f'{self.user} - Product {original_product.SKU} - Add product option "{link.product_option_value}".'
                )
                updater.set_product_option_link(link.product_option_value)
