"""Update Products in the database and Cloud Commerce."""


import logging

from ccapi import CCAPI

from inventory import models

from .base_updater import BaseCloudCommerceUpdater


class BaseProductUpdater(BaseCloudCommerceUpdater):
    """Base updater for updating products."""

    SUPPLIER_SKU_PRODUCT_OPTION_ID = 34627
    PURCHASE_PRICE_PRODUCT_OPTION_ID = 35132
    RETAIL_PRICE_PRODUCT_OPTION_ID = 54879
    LENGTH_PRODUCT_OPTION_ID = 61989
    HEIGHT_PRODUCT_OPTION_ID = 61988
    WIDTH_PRODUCT_OPTION_ID = 61990
    DATE_CREATED_PRODUCT_OPTION_ID = 41023

    def set_supplier(self, supplier):
        """
        Set the product's supplier.

        args:
            supplier (inventory.models.suppliers.Supplier)

        """
        args, kwargs = self._prepare_set_supplier(supplier)
        if self.update_DB:
            self._set_DB_supplier(*args, **kwargs)
        if self.update_CC:
            self._set_CC_supplier(*args, **kwargs)

    def set_supplier_SKU(self, supplier_SKU):
        """Set the product's supplier SKU."""
        args, kwargs = self._prepare_set_supplier_SKU(supplier_SKU)
        if self.update_DB:
            self._set_DB_supplier_SKU(supplier_SKU)
        if self.update_CC:
            self._set_CC_supplier_SKU(supplier_SKU)

    def set_barcode(self, barcode):
        """Set the product's barcode."""
        args, kwargs = self._prepare_set_barcode(barcode)
        if self.update_DB:
            self._set_DB_barcode(*args, **kwargs)
        if self.update_CC:
            self._set_CC_barcode(*args, **kwargs)

    def set_purchase_price(self, purchase_price):
        """Set the product's purchase price."""
        args, kwargs = self._prepare_set_purchase_price(purchase_price)
        if self.update_DB:
            self._set_DB_purchase_price(*args, **kwargs)
        if self.update_CC:
            self._set_CC_purchase_price(*args, **kwargs)

    def set_VAT_rate(self, VAT_rate):
        """
        Set the product's VAT rate.

        args:
            VAT_rate (inventory.models.vat_rates.VATRate)

        """
        args, kwargs = self._prepare_set_VAT_rate(VAT_rate)
        if self.update_DB:
            self._set_DB_VAT_rate(*args, **kwargs)
        if self.update_CC:
            self._set_CC_VAT_rate(*args, **kwargs)

    def set_price(self, price):
        """Set the product's price."""
        args, kwargs = self._prepare_set_price(price)
        if self.update_DB:
            self._set_DB_price(*args, **kwargs)
        if self.update_CC:
            self._set_CC_price(*args, **kwargs)

    def set_retail_price(self, retail_price):
        """Set the product's retail price."""
        args, kwargs = self._prepare_set_retail_price(retail_price)
        if self.update_DB:
            self._set_DB_retail_price(*args, **kwargs)
        if self.update_CC:
            self._set_CC_retail_price(*args, **kwargs)

    def set_brand(self, brand):
        """
        Set the product's brand.

        args:
            brand (inventory.models.product_options.Brand)

        """
        args, kwargs = self._prepare_set_brand(brand)
        if self.update_DB:
            self._set_DB_brand(*args, **kwargs)
        if self.update_CC:
            self._set_CC_brand(*args, **kwargs)

    def set_manufacturer(self, manufacturer):
        """
        Set the product's manufacturer.

        args:
            manufacturer (inventory.models.product_options.Manufacturer)

        """
        args, kwargs = self._prepare_set_manufacturer(manufacturer)
        if self.update_DB:
            self._set_DB_manufacturer(*args, **kwargs)
        if self.update_CC:
            self._set_CC_manufacturer(*args, **kwargs)

    def set_package_type(self, package_type):
        """
        Set the product's package type.

        args:
            package_type (inventory.models.product_options.PackageType)

        """
        args, kwargs = self._prepare_set_package_type(package_type)
        if self.update_DB:
            self._set_DB_package_type(*args, **kwargs)
        if self.update_CC:
            self._set_CC_package_type(*args, **kwargs)

    def set_international_shipping(self, international_shipping):
        """
        Set the product's international shipping.

        args:
            international_shipping (inventory.models.product_options.InternationalShipping)

        """
        args, kwargs = self._prepare_set_international_shipping(international_shipping)
        if self.update_DB:
            self._set_DB_international_shipping(*args, **kwargs)
        if self.update_CC:
            self._set_CC_international_shipping(*args, **kwargs)

    def set_bays(self, bays):
        """
        Set the bays in which the product is stocked.

        args:
            bays (list(inventory.models.locations.Bay))

        """
        args, kwargs = self._prepare_set_bays(bays)
        if self.update_DB:
            self._set_DB_bays(*args, **kwargs)
        if self.update_CC:
            self._set_CC_bays(*args, **kwargs)

    def set_weight(self, weight):
        """Set the product's weight in grams."""
        args, kwargs = self._prepare_set_weight(weight)
        if self.update_DB:
            self._set_DB_weight(*args, **kwargs)
        if self.update_CC:
            self._set_CC_weight(*args, **kwargs)

    def set_length(self, length):
        """Set the product's length in milimeters."""
        args, kwargs = self._prepare_set_length(length)
        if self.update_DB:
            self._set_DB_length(*args, **kwargs)
        if self.update_CC:
            self._set_CC_length(*args, **kwargs)

    def set_height(self, height):
        """Set the product's height in milimeters."""
        args, kwargs = self._prepare_set_height(height)
        if self.update_DB:
            self._set_DB_height(*args, **kwargs)
        if self.update_CC:
            self._set_CC_height(*args, **kwargs)

    def set_width(self, width):
        """Set the product's width in milimeters."""
        args, kwargs = self._prepare_set_width(width)
        if self.update_DB:
            self._set_DB_width(*args, **kwargs)
        if self.update_CC:
            self._set_CC_width(*args, **kwargs)

    def set_gender(self, gender):
        """Set the product's Gender."""
        args, kwargs = self._prepare_set_gender(gender)
        if self.update_DB:
            self._set_DB_gender(*args, **kwargs)
        if self.update_CC:
            self._set_CC_gender(*args, **kwargs)

    def set_product_option_link(self, product_option_value):
        """
        Set or change the value for one of the product's product options.

        args:
            product_option_value (inventory.models.product_options.ProductOptionValue)

        """
        args, kwargs = self._prepare_set_product_option_link(product_option_value)
        if self.update_DB:
            self._set_DB_product_option_link(*args, **kwargs)
        if self.update_CC:
            self._set_CC_product_option_link(*args, **kwargs)

    def remove_product_option_link(self, product_option_value):
        """Remove a product option link from the product."""
        args, kwargs = self._prepare_remove_product_option_link(product_option_value)
        if self.update_DB:
            self._remove_DB_product_option_link(*args, **kwargs)
        if self.update_CC:
            self._remove_CC_product_option_link(*args, **kwargs)

    def set_date_created(self):
        """Set the date on which the product was created."""
        args, kwargs = self._prepare_set_date_created()
        if self.update_CC:
            self._set_CC_date_created(*args, **kwargs)

    def _prepare_set_supplier(self, supplier):
        self.log(f"Set supplier to {supplier}.")
        return [supplier], {}

    def _prepare_set_supplier_SKU(self, supplier_SKU):
        self.log(f"Set supplier SKU to {supplier_SKU}.")
        return [supplier_SKU], {}

    def _prepare_set_barcode(self, barcode):
        self.log(f"Set barcode to {barcode}.")
        return [barcode], {}

    def _prepare_set_purchase_price(self, purchase_price):
        self.log(f"Set purchase price to {purchase_price}.")
        return [purchase_price], {}

    def _prepare_set_VAT_rate(self, VAT_rate):
        self.log(f"Set VAT rate to {VAT_rate}.")
        return [VAT_rate], {}

    def _prepare_set_price(self, price):
        self.log(f"Set price to {price}.")
        return [price], {}

    def _prepare_set_retail_price(self, retail_price):
        self.log(f"Set retail price to {retail_price}.")
        return [retail_price], {}

    def _prepare_set_brand(self, brand):
        self.log(f"Set brand to {brand}.")
        return [brand], {}

    def _prepare_set_manufacturer(self, manufacturer):
        self.log(f"Set manufacturer to {manufacturer}.")
        return [manufacturer], {}

    def _prepare_set_package_type(self, package_type):
        self.log(f"Set package type to {package_type}.")
        return [package_type], {}

    def _prepare_set_international_shipping(self, international_shipping):
        self.log(f"Set international shipping to {international_shipping}.")
        return [international_shipping], {}

    def _prepare_set_bays(self, bays):
        self.log(f"Set bays to {list(bays)}.")
        return [bays], {}

    def _prepare_set_weight(self, weight):
        self.log(f"Set weight to {weight}.")
        return [weight], {}

    def _prepare_set_length(self, length):
        self.log(f"Set length to {length}.")
        return [length], {}

    def _prepare_set_height(self, height):
        self.log(f"Set height to {height}.")
        return [height], {}

    def _prepare_set_width(self, width):
        self.log(f"Set width to {width}.")
        return [width], {}

    def _prepare_set_gender(self, gender):
        self.log(f"Set gender to {gender}.")
        return [gender], {}

    def _prepare_set_product_option_link(self, product_option_value):
        self.log(
            f'Set product option "{product_option_value.product_option}" to '
            f'"{product_option_value.value}"'
        )
        return [product_option_value], {}

    def _prepare_remove_product_option_link(self, product_option_value):
        self.log(f'Remove product option "{product_option_value.product_option}".')
        return [product_option_value], {}

    def _prepare_set_date_created(self):
        self.log(
            f"Set date created to {self.db_object.date_created} on Cloud Commerce."
        )
        return [self.db_object.date_created], {}

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
        if retail_price is None:
            self._clear_CC_product_options(self.RETAIL_PRICE_PRODUCT_OPTION_ID)
        else:
            value = "{:.2f}".format(retail_price)
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
        link, created = self.product_option_value_link_model.objects.filter(
            product=self.db_object,
            product_option_value__product_option=product_option_value.product_option,
        ).delete()
        self.product_option_value_link_model.objects.create(
            product=self.db_object, product_option_value=product_option_value
        )

    def _set_CC_product_option_link(self, product_option_value):
        self._set_CC_product_option(
            product_option_ID=product_option_value.product_option.product_option_ID,
            product_option_value_ID=product_option_value.product_option_value_ID,
        )

    def _remove_DB_product_option_link(self, product_option_value):
        self.product_option_value_link_model.objects.filter(
            product=self.db_object,
            product_option_value__product_option=product_option_value.product_option,
        ).delete()

    def _remove_CC_product_option_link(self, product_option_value):
        self._clear_CC_product_options(
            product_option_value.product_option.product_option_ID
        )

    def _set_CC_date_created(self, date):
        date_string = date.strftime("%Y-%m-%d")
        self._set_or_create_CC_product_option(
            product_option_ID=self.DATE_CREATED_PRODUCT_OPTION_ID, value=date_string
        )


class ProductUpdater(BaseProductUpdater):
    """Update a Product in the database and in Cloud Commerce."""

    LOG_MESSAGE = "{} - Product {} - {}"
    update_DB = True
    update_CC = True

    product_option_value_link_model = models.ProductOptionValueLink


class PartialProductUpdater(BaseProductUpdater):
    """Update a Partial Product in the database."""

    LOGGING_LEVEL = logging.DEBUG
    LOG_MESSAGE = "{} - Partial Product {} - {}"

    update_DB = True
    update_CC = False

    product_option_value_link_model = models.PartialProductOptionValueLink
