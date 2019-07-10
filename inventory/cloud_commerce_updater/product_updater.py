"""Update Products in the database and Cloud Commerce."""

from ccapi import CCAPI

from inventory import models

from .base_updater import BaseCloudCommerceUpdater


class ProductUpdater(BaseCloudCommerceUpdater):
    """Update a Product in the database and in Cloud Commerce."""

    SUPPLIER_SKU_PRODUCT_OPTION_ID = 34627
    PURCHASE_PRICE_PRODUCT_OPTION_ID = 35132
    RETAIL_PRICE_PRODUCT_OPTION_ID = 54879
    LENGTH_PRODUCT_OPTION_ID = 61989
    HEIGHT_PRODUCT_OPTION_ID = 61988
    WIDTH_PRODUCT_OPTION_ID = 61990
    DATE_CREATED_PRODUCT_OPTION_ID = 41023

    def __init__(self, db_object):
        """
        Instantiate the Product Updater.

        args:
            db_object (inventory.models.products.Product)
        """
        super().__init__(db_object)

    def set_supplier(self, supplier):
        """
        Set the product's supplier.

        args:
            supplier (inventory.models.suppliers.Supplier)
        """
        self._set_DB_supplier(supplier)
        self._set_CC_supplier(supplier)

    def set_supplier_SKU(self, supplier_SKU: str):
        """Set the product's supplier SKU."""
        self._set_DB_supplier_SKU(supplier_SKU)
        self._set_CC_supplier_SKU(supplier_SKU)

    def set_barcode(self, barcode: str):
        """Set the product's barcode."""
        self._set_DB_barcode(barcode)
        self._set_CC_barcode(barcode)

    def set_purchase_price(self, purchase_price):
        """Set the product's purchase price."""
        self._set_DB_purchase_price(purchase_price)
        self._set_CC_purchase_price(purchase_price)

    def set_VAT_rate(self, VAT_rate):
        """
        Set the product's VAT rate.

        args:
            VAT_rate (inventory.models.vat_rates.VATRate)
        """
        self._set_DB_VAT_rate(VAT_rate)
        self._set_CC_VAT_rate(VAT_rate)

    def set_price(self, price):
        """Set the product's price."""
        self._set_DB_price(price)
        self._set_CC_price(price)

    def set_retail_price(self, retail_price):
        """Set the product's retail price."""
        self._set_DB_retail_price(retail_price)
        self._set_CC_retail_price(retail_price)

    def set_brand(self, brand):
        """
        Set the product's brand.

        args:
            brand (inventory.models.product_options.Brand)
        """
        self._set_DB_brand(brand)
        self._set_CC_brand(brand)

    def set_manufacturer(self, manufacturer):
        """
        Set the product's manufacturer.

        args:
            manufacturer (inventory.models.product_options.Manufacturer)
        """
        self._set_DB_manufacturer(manufacturer)
        self._set_CC_manufacturer(manufacturer)

    def set_package_type(self, package_type):
        """
        Set the product's package type.

        args:
            package_type (inventory.models.product_options.PackageType)
        """
        self._set_DB_package_type(package_type)
        self._set_CC_package_type(package_type)

    def set_international_shipping(self, international_shipping):
        """
        Set the product's international shipping.

        args:
            international_shipping (inventory.models.product_options.InternationalShipping)
        """
        self._set_DB_international_shipping(international_shipping)
        self._set_CC_international_shipping(international_shipping)

    def set_bays(self, bays):
        """
        Set the bays in which the product is stocked.

        args:
            bays (list(inventory.models.locations.Bay))
        """
        self._set_DB_bays(bays)
        self._set_CC_bays(bays)

    def set_weight(self, weight: int):
        """Set the product's weight in grams."""
        self._set_DB_weight(weight)
        self._set_CC_weight(weight)

    def set_length(self, length: int):
        """Set the product's length in milimeters."""
        self._set_DB_length(length)
        self._set_CC_length(length)

    def set_height(self, height: int):
        """Set the product's height in milimeters."""
        self._set_DB_height(height)
        self._set_CC_height(height)

    def set_width(self, width: int):
        """Set the product's width in milimeters."""
        self._set_DB_width(width)
        self._set_CC_width(width)

    def set_gender(self, gender):
        """Set the product's Gender."""
        self._set_DB_gender(gender)
        self._set_CC_gender(gender)

    def set_product_option_link(self, product_option_value):
        """
        Set or change the value for one of the product's product options.

        args:
            product_option_value (inventory.models.product_options.ProductOptionValue)
        """
        self._set_DB_product_option_link(product_option_value)
        self._set_CC_product_option_link(product_option_value)

    def set_date_created(self):
        """Set the date on which the product was created."""
        self._set_CC_date_created(self.db_object.date_created)

    def _set_CC_product_option(self, *, product_option_ID, product_option_value_ID):
        CCAPI.set_product_option_value(
            product_ids=[self.db_object.product_ID],
            option_id=product_option_ID,
            option_value_id=product_option_value_ID,
        )

    def _clear_CC_product_options(self, product_option_ID):
        self._set_CC_product_option(
            product_option_ID=product_option_ID, product_option_value_ID=0
        )

    def _set_or_create_CC_product_option(self, *, product_option_ID, value):
        product_option_value_ID = CCAPI.get_option_value_id(
            option_id=product_option_ID, value=value, create=True
        )
        self._set_CC_product_option(
            product_option_ID=product_option_ID,
            product_option_value_ID=product_option_value_ID,
        )

    def _clear_factory_links(self):
        factory_links = CCAPI.get_product_factory_links(self.db_object.product_ID)
        for link in factory_links:
            CCAPI.delete_product_factory_link(link.link_id)

    def _set_DB_supplier(self, supplier):
        self.db_object.supplier = supplier
        self.db_object.save()

    def _set_CC_supplier(self, supplier):
        self._clear_factory_links()
        CCAPI.update_product_factory_link(
            product_id=self.db_object.product_ID,
            factory_id=supplier.factory_ID,
            dropship=False,
            supplier_sku=self.db_object.supplier_SKU or "",
            price=self.db_object.purchase_price,
        )
        self._set_CC_product_option(
            product_option_ID=supplier.PRODUCT_OPTION_ID,
            product_option_value_ID=supplier.product_option_value_ID,
        )

    def _set_DB_supplier_SKU(self, supplier_SKU):
        self.db_object.supplier_SKU = supplier_SKU or None
        self.db_object.save()

    def _set_CC_supplier_SKU(self, supplier_SKU):
        self._set_or_create_CC_product_option(
            product_option_ID=self.SUPPLIER_SKU_PRODUCT_OPTION_ID,
            value=supplier_SKU or "",
        )

    def _set_DB_barcode(self, barcode):
        self.db_object.barcode = barcode
        self.db_object.save()

    def _set_CC_barcode(self, barcode):
        CCAPI.set_product_barcode(product_id=self.db_object.product_ID, barcode=barcode)

    def _set_DB_purchase_price(self, purchase_price):
        self.db_object.purchase_price = purchase_price
        self.db_object.save()

    def _set_CC_purchase_price(self, purchase_price):
        self._set_or_create_CC_product_option(
            product_option_ID=self.PURCHASE_PRICE_PRODUCT_OPTION_ID,
            value="{:.2f}".format(purchase_price),
        )

    def _set_DB_VAT_rate(self, VAT_rate):
        self.db_object.VAT_rate = VAT_rate
        self.db_object.save()

    def _set_CC_VAT_rate(self, VAT_rate):
        CCAPI.set_product_vat_rate_by_id(
            product_ids=[self.db_object.product_ID], vat_rate_id=VAT_rate.VAT_rate_ID
        )

    def _set_DB_price(self, price):
        self.db_object.price = price
        self.db_object.save()

    def _set_CC_price(self, price):
        CCAPI.set_product_base_price(product_id=self.db_object.product_ID, price=price)

    def _set_DB_retail_price(self, retail_price):
        self.db_object.retail_price = retail_price
        self.db_object.save()

    def _set_CC_retail_price(self, retail_price):
        if retail_price:
            value = "{:.2f}".format(retail_price)
        else:
            value = ""
        self._set_or_create_CC_product_option(
            product_option_ID=self.RETAIL_PRICE_PRODUCT_OPTION_ID, value=value
        )

    def _set_DB_brand(self, brand):
        self.db_object.brand = brand
        self.db_object.save()

    def _set_CC_brand(self, brand):
        self._set_CC_product_option(
            product_option_ID=brand.PRODUCT_OPTION_ID,
            product_option_value_ID=brand.product_option_value_ID,
        )

    def _set_DB_manufacturer(self, manufacturer):
        self.db_object.manufacturer = manufacturer
        self.db_object.save()

    def _set_CC_manufacturer(self, manufacturer):
        self._set_CC_product_option(
            product_option_ID=manufacturer.PRODUCT_OPTION_ID,
            product_option_value_ID=manufacturer.product_option_value_ID,
        )

    def _set_DB_package_type(self, package_type):
        self.db_object.package_type = package_type
        self.db_object.save()

    def _set_CC_package_type(self, package_type):
        self._set_CC_product_option(
            product_option_ID=package_type.PRODUCT_OPTION_ID,
            product_option_value_ID=package_type.product_option_value_ID,
        )
        CCAPI.set_product_scope(
            product_id=self.db_object.product_ID,
            weight=self.db_object.weight_grams,
            height=0,
            length=0,
            width=0,
            large_letter_compatible=package_type.large_letter_compatible,
        )

    def _set_DB_international_shipping(self, international_shipping):
        self.db_object.international_shipping = international_shipping
        self.db_object.save()

    def _set_CC_international_shipping(self, international_shipping):
        self._set_CC_product_option(
            product_option_ID=international_shipping.PRODUCT_OPTION_ID,
            product_option_value_ID=international_shipping.product_option_value_ID,
        )

    def _set_DB_bays(self, bays):
        self.db_object.bays.set(bays)
        self.db_object.save()

    def _set_CC_bays(self, bays):
        updated_bays = [_.bay_ID for _ in bays]
        existing_bays = [
            str(_.id) for _ in CCAPI.get_bays_for_product(self.db_object.product_ID)
        ]
        bays_to_remove = [_ for _ in existing_bays if _ not in updated_bays]
        bays_to_add = [_ for _ in updated_bays if _ not in existing_bays]
        for bay_ID in bays_to_remove:
            CCAPI.remove_warehouse_bay_from_product(self.db_object.product_ID, bay_ID)
        for bay_ID in bays_to_add:
            CCAPI.add_warehouse_bay_to_product(self.db_object.product_ID, bay_ID)

    def _set_DB_weight(self, weight):
        self.db_object.weight_grams = weight
        self.db_object.save()

    def _set_CC_weight(self, weight):
        CCAPI.set_product_scope(
            product_id=self.db_object.product_ID,
            weight=weight,
            height=0,
            length=0,
            width=0,
            large_letter_compatible=self.db_object.package_type.large_letter_compatible,
        )

    def _set_DB_length(self, length):
        self.db_object.length_mm = length
        self.db_object.save()

    def _set_CC_length(self, length):
        self._set_or_create_CC_product_option(
            product_option_ID=self.LENGTH_PRODUCT_OPTION_ID, value=str(length)
        )

    def _set_DB_height(self, height):
        self.db_object.height_mm = height
        self.db_object.save()

    def _set_CC_height(self, height):
        self._set_or_create_CC_product_option(
            product_option_ID=self.HEIGHT_PRODUCT_OPTION_ID, value=str(height)
        )

    def _set_DB_width(self, width):
        self.db_object.width_mm = width
        self.db_object.save()

    def _set_CC_width(self, width):
        self._set_or_create_CC_product_option(
            product_option_ID=self.WIDTH_PRODUCT_OPTION_ID, value=str(width)
        )

    def _set_DB_gender(self, gender):
        self.db_object.gender = gender
        self.db_object.save()

    def _set_CC_gender(self, gender):
        if gender is None:
            self._clear_CC_product_options(
                product_option_ID=models.Gender.PRODUCT_OPTION_ID
            )
        else:
            self._set_CC_product_option(
                product_option_ID=gender.PRODUCT_OPTION_ID,
                product_option_value_ID=gender.product_option_value_ID,
            )

    def _set_DB_product_option_link(self, product_option_value):
        link, created = models.ProductOptionValueLink.objects.get_or_create(
            product=self.db_object,
            product_option_value__product_option=product_option_value.product_option,
            defaults={"product_option_value": product_option_value},
        )
        if link.product_option_value != product_option_value:
            link.product_option_value = product_option_value
            link.save()

    def _set_CC_product_option_link(self, product_option_value):
        self._set_CC_product_option(
            product_option_ID=product_option_value.product_option.product_option_ID,
            product_option_value_ID=product_option_value.product_option_value_ID,
        )

    def _set_CC_date_created(self, date):
        date_string = date.strftime("%Y-%m-%d")
        self._set_or_create_CC_product_option(
            product_option_ID=self.DATE_CREATED_PRODUCT_OPTION_ID, value=date_string
        )


class PartialProductUpdater(BaseCloudCommerceUpdater):
    """Update a Partial Product in the database."""

    def set_supplier(self, supplier):
        """
        Set the product's supplier.

        args:
            supplier (inventory.models.suppliers.Supplier)
        """
        self._set_DB_supplier(supplier)

    def set_supplier_SKU(self, supplier_SKU: str):
        """Set the product's supplier SKU."""
        self._set_DB_supplier_SKU(supplier_SKU)

    def set_barcode(self, barcode: str):
        """Set the product's barcode."""
        self._set_DB_barcode(barcode)

    def set_purchase_price(self, purchase_price):
        """Set the product's purchase price."""
        self._set_DB_purchase_price(purchase_price)

    def set_VAT_rate(self, VAT_rate):
        """
        Set the product's VAT rate.

        args:
            VAT_rate (inventory.models.vat_rates.VATRate)
        """
        self._set_DB_VAT_rate(VAT_rate)

    def set_price(self, price):
        """Set the product's price."""
        self._set_DB_price(price)

    def set_retail_price(self, retail_price):
        """Set the product's retail price."""
        self._set_DB_retail_price(retail_price)

    def set_brand(self, brand):
        """
        Set the product's brand.

        args:
            brand (inventory.models.product_options.Brand)
        """
        self._set_DB_brand(brand)

    def set_manufacturer(self, manufacturer):
        """
        Set the product's manufacturer.

        args:
            manufacturer (inventory.models.product_options.Manufacturer)
        """
        self._set_DB_manufacturer(manufacturer)

    def set_package_type(self, package_type):
        """
        Set the product's package type.

        args:
            package_type (inventory.models.product_options.PackageType)
        """
        self._set_DB_package_type(package_type)

    def set_international_shipping(self, international_shipping):
        """
        Set the product's international shipping.

        args:
            international_shipping (inventory.models.product_options.InternationalShipping)
        """
        self._set_DB_international_shipping(international_shipping)

    def set_bays(self, bays):
        """
        Set the bays in which the product is stocked.

        args:
            bays (list(inventory.models.locations.Bay))
        """
        self._set_DB_bays(bays)

    def set_weight(self, weight: int):
        """Set the product's weight in grams."""
        self._set_DB_weight(weight)

    def set_length(self, length: int):
        """Set the product's length in milimeters."""
        self._set_DB_length(length)

    def set_height(self, height: int):
        """Set the product's height in milimeters."""
        self._set_DB_height(height)

    def set_width(self, width: int):
        """Set the product's width in milimeters."""
        self._set_DB_width(width)

    def set_gender(self, gender):
        """Set the product's Gender."""
        self._set_DB_gender(gender)

    def set_product_option_link(self, product_option_value):
        """
        Set or change the value for one of the product's product options.

        args:
            product_option_value (inventory.models.product_options.ProductOptionValue)
        """
        self._set_DB_product_option_link(product_option_value)
