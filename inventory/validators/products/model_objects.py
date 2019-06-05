"""Validate inventory.Product model objects."""


from validation import BaseObjectValidator, BaseValidationCheck, Levels


class ProductObjectValidationCheck(BaseValidationCheck):
    """Base validation checker for Product model objects."""

    requires_matching = True

    def get_matching_product(self, model_object):
        """
        Return the matching Product Export rows for a Product model instance.

        Return None if no matching Product exists in the export.
        """
        return self.validation_runner.product_lookup.get(model_object.SKU)

    def get_test_data(self, *args, **kwargs):
        """Get required objects for testing."""
        test_data = super().get_test_data(*args, **kwargs)
        self.db_product = test_data["test_object"]
        if self.requires_matching:
            self.export_product = self.get_matching_product(self.db_product)
        return test_data


class ProductModelObjectValidator(BaseObjectValidator):
    """Validate the Product model."""

    name = "Product Model"
    validation_check_class = ProductObjectValidationCheck

    def get_test_objects(self, validation_runner):
        """Run validation for all Product model objects."""
        return validation_runner.model_objects


class ProductExists(ProductObjectValidationCheck):
    """Check a Product exists in Cloud Commerce."""

    name = "Product missing from Cloud Commerce"
    level = Levels.ERROR

    def is_valid(self, *args, **kwargs):
        """Check a Product with the same SKU exists in Cloud Commerce."""
        if self.db_product is None:
            return False
        else:
            return True

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        return (
            f"No Product exists in Cloud Commerce with the SKU "
            f'"{self.db_product.SKU}".'
        )


class ProductRangeMatches(ProductObjectValidationCheck):
    """Check a Product is in the same Range in the database and Cloud Commerce."""

    name = "Product is in a different Range."
    level = Levels.ERROR

    def is_valid(self, *args, **kwargs):
        """Check a Product is in the same Range in the database and Cloud Commerce."""
        if self.export_product is None:
            return True
        if self.db_product.product_range.SKU != self.export_product.range_SKU:
            return False
        else:
            return True

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        return (
            f'The Product "{self.db_product.SKU}" is part of the Range '
            f'{self.db_product.product_range.SKU}" in the database but is part of the '
            f'Range "{self.export_product.range_SKU}" in Cloud Commerce.'
        )


class ProductBaysMatch(ProductObjectValidationCheck):
    """Check the bay links for a database product match those in Cloud Commerce."""

    name = "Product bays do not match"
    level = Levels.ERROR

    def get_test_data(self, *args, **kwargs):
        """Return dict of validation test variables."""
        test_data = super().get_test_data(*args, **kwargs)
        if self.export_product is not None:
            self.db_bay_names = sorted(
                self.db_product.bays.values_list("name", flat=True)
            )
            self.cc_bay_names = sorted(self.export_product.bays)
        return test_data

    def is_valid(self, *args, **kwargs):
        """Check the bay links for a database product match those in Cloud Commerce."""
        if self.export_product is None or self.db_bay_names == self.cc_bay_names:
            return True
        else:
            return False

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        db_bay_names = ", ".join((f"{_}" for _ in self.db_bay_names))
        cc_bay_names = ", ".join((f"{_}" for _ in self.cc_bay_names))
        return (
            f'The bays linked with the database product "{self.db_product.SKU}" '
            f"({db_bay_names}) do not match those in Cloud Commerce ({cc_bay_names})."
        )


class ProductBarcodeMatches(ProductObjectValidationCheck):
    """Check a products barcode in the database matches Cloud Commerce."""

    name = "Product barcodes do not match"
    level = Levels.ERROR

    def is_valid(self, *args, **kwargs):
        """Check a products barcode in the database matches Cloud Commerce."""
        if self.export_product is None:
            return True
        else:
            return self.db_product.barcode == self.export_product.barcode

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        return (
            f'The barcode of Product "{self.db_product}" '
            f'("{self.db_product.barcode}") does not match Cloud Commerce '
            f'("{self.export_product.barcode}").'
        )


class ProductPriceMatches(ProductObjectValidationCheck):
    """Check a products price in the database matches Cloud Commerce."""

    name = "Product prices do not match"
    level = Levels.ERROR

    def get_test_data(self, *args, **kwargs):
        """Return dict of validation test variables."""
        test_data = super().get_test_data(*args, **kwargs)
        if self.export_product is not None:
            self.db_price = round(float(self.db_product.price), 2)
            try:
                self.export_price = round(float(self.export_product.price), 2)
            except ValueError:
                self.export_price = str(self.export_product.price)
        return test_data

    def is_valid(self, *args, **kwargs):
        """Check a products barcode in the database matches Cloud Commerce."""
        if self.export_product is None:
            return True
        else:
            return self.db_price == self.export_price

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        return (
            f'The price of Product "{self.db_product}" ("{self.db_price}") does not '
            f'match Cloud Commerce ("{self.export_price}").'
        )


class ProductVATRateMatches(ProductObjectValidationCheck):
    """Check a products VAT rate in the database matches Cloud Commerce."""

    name = "Product VAT Rates do not match"
    level = Levels.ERROR

    def is_valid(self, *args, **kwargs):
        """Check a products VAT rate in the database matches Cloud Commerce."""
        if self.export_product is None:
            return True
        return self.db_product.VAT_rate.percentage == float(
            self.export_product.VAT_rate
        )

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        return (
            f'The VAT rate of Product "{self.db_product}" '
            f'("{self.db_product.VAT_rate.percentage}") '
            f'does not match Cloud Commerce ("{self.export_product.VAT_rate}").'
        )


class ProductSupplierMatches(ProductObjectValidationCheck):
    """Check a products Factory in the database matches Cloud Commerce."""

    name = "Product suppliers do not match"
    level = Levels.ERROR

    def is_valid(self, *args, **kwargs):
        """Check a products supplier in the database matches Cloud Commerce."""
        if self.export_product is None:
            return True
        return self.db_product.supplier.name == self.export_product.factory

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        return (
            f'The Supplier of Product "{self.db_product}" '
            f'("{self.db_product.supplier.name}") '
            f'does not match Cloud Commerce ("{self.export_product.factory}").'
        )


class ProductWeightMatches(ProductObjectValidationCheck):
    """Check a products Weight in the database matches Cloud Commerce."""

    name = "Product weights do not match"
    level = Levels.ERROR

    def is_valid(self, *args, **kwargs):
        """Check a products weight in the database matches Cloud Commerce."""
        if self.export_product is None:
            return True
        return self.db_product.weight_grams == float(self.export_product.weight)

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        return (
            f'The Weight of Product "{self.db_product}" '
            f'("{self.db_product.weight_grams}") '
            f'does not match Cloud Commerce ("{self.export_product.weight}").'
        )


class ProductDimensionsMatch(ProductObjectValidationCheck):
    """Check a products Dimensions in the database matches Cloud Commerce."""

    name = "Product weights do not match"
    level = Levels.ERROR

    def is_valid(self, *args, **kwargs):
        """Check a products weight in the database matches Cloud Commerce."""
        if self.export_product is None:
            return True
        if self.db_product.height_mm != float(self.export_product.height):
            return False
        if self.db_product.length_mm != float(self.export_product.length):
            return False
        if self.db_product.width_mm != float(self.export_product.width):
            return False
        return True

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        db_dimensions = "H: {}, L: {}, W: {}".format(
            self.db_product.height_mm,
            self.db_product.length_mm,
            self.db_product.width_mm,
        )
        export_dimensions = "H: {}, L: {}, W: {}".format(
            self.export_product.height,
            self.export_product.length,
            self.export_product.width,
        )
        return (
            f'The Dimensions of Product "{self.db_product}" '
            f'("{db_dimensions}") '
            f'does not match Cloud Commerce ("{export_dimensions}").'
        )


class ProductPackageTypesMatch(ProductObjectValidationCheck):
    """Check a products Package Type matches Cloud Commerce."""

    name = "Product Package Types do not match"
    level = Levels.ERROR

    def is_valid(self, *args, **kwargs):
        """Check a products Package Type matches Cloud Commerce."""
        if self.export_product is None:
            return True
        return self.db_product.package_type.name == self.export_product.package_type

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        return (
            f'The Package Type of Product "{self.db_product}" '
            f'("{self.db_product.package_type.name}") does not match the one in Cloud '
            f'Commerce ("{self.export_product.package_type}").'
        )


class ProductInternationalShippingMatches(ProductObjectValidationCheck):
    """Check a products International Shipping matches Cloud Commerce."""

    name = "Product International Shipping does not match"
    level = Levels.ERROR

    def is_valid(self, *args, **kwargs):
        """Check a products International Shipping matches Cloud Commerce."""
        if self.export_product is None:
            return True
        return (
            self.db_product.international_shipping.name
            == self.export_product.international_shipping
        )

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        return (
            f'The International Shipping of Product "{self.db_product}" '
            f'("{self.db_product.international_shipping.name}") does not match the one '
            f'in Cloud Commerce ("{self.export_product.international_shipping}").'
        )


class ProductDepartmentMatches(ProductObjectValidationCheck):
    """Check a products Department matches Cloud Commerce."""

    name = "Product Department does not match"
    level = Levels.ERROR

    def is_valid(self, *args, **kwargs):
        """Check a products Department matches Cloud Commerce."""
        if self.export_product is None:
            return True
        return (
            self.db_product.product_range.department.name
            == self.export_product.department
        )

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        return (
            f'The Department of Product "{self.db_product}" '
            f'("{self.db_product.product_range.department.name}") does not match the '
            f'one in Cloud Commerce ("{self.export_product.department}").'
        )


class ProductBrandMatches(ProductObjectValidationCheck):
    """Check a products Brand matches Cloud Commerce."""

    name = "Product Brand does not match"
    level = Levels.ERROR

    def is_valid(self, *args, **kwargs):
        """Check a products Department matches Cloud Commerce."""
        if self.export_product is None:
            return True
        return self.db_product.brand.name == self.export_product.brand

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        return (
            f'The Brand of Product "{self.db_product}" '
            f'("{self.db_product.brand.name}") does not match the '
            f'one in Cloud Commerce ("{self.export_product.brand}").'
        )


class ProductManufacturerMatches(ProductObjectValidationCheck):
    """Check a products Manufacturer matches Cloud Commerce."""

    name = "Product Manufacturer does not match"
    level = Levels.ERROR

    def is_valid(self, *args, **kwargs):
        """Check a products Manufacturer matches Cloud Commerce."""
        if self.export_product is None:
            return True
        return self.db_product.manufacturer.name == self.export_product.manufacturer

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        return (
            f'The Manufacturer of Product "{self.db_product}" '
            f'("{self.db_product.manufacturer.name}") does not match the '
            f'one in Cloud Commerce ("{self.export_product.manufacturer}").'
        )


class ProductSupplierSKUMatches(ProductObjectValidationCheck):
    """Check a products Supplier SKU matches Cloud Commerce."""

    name = "Product Supplier SKU does not match"
    level = Levels.ERROR

    def is_valid(self, *args, **kwargs):
        """Check a products Supplier SKU matches Cloud Commerce."""
        if self.export_product is None:
            return True
        return self.db_product.supplier_SKU == self.export_product.supplier_SKU

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        return (
            f'The supplier SKU of Product "{self.db_product}" '
            f'("{self.db_product.supplier_SKU}") does not match the '
            f'one in Cloud Commerce ("{self.export_product.supplier_SKU}").'
        )


class ProductPurchasePriceMatches(ProductObjectValidationCheck):
    """Check a products Pruchase Price matches Cloud Commerce."""

    name = "Product Purchase Price does not match"
    level = Levels.ERROR

    def get_test_data(self, *args, **kwargs):
        """Return dict of validation test variables."""
        test_data = super().get_test_data(*args, **kwargs)
        if self.export_product is not None:
            self.db_price = round(float(self.db_product.purchase_price), 2)
            try:
                self.export_price = round(float(self.export_product.purchase_price), 2)
            except ValueError:
                self.export_price = str(self.export_product.purchase_price)
        return test_data

    def is_valid(self, *args, **kwargs):
        """Check a products Purchase Price matches Cloud Commerce."""
        if self.export_product is None:
            return True
        return self.db_price == self.export_price

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        return (
            f'The Purchase Price of Product "{self.db_product}" '
            f'("{self.db_price}") does not match the '
            f'one in Cloud Commerce ("{self.export_price}").'
        )


class ProductRetailPriceMatches(ProductObjectValidationCheck):
    """Check a products Retail Price matches Cloud Commerce."""

    name = "Product Retail Price does not match"
    level = Levels.ERROR

    def get_test_data(self, *args, **kwargs):
        """Return dict of validation test variables."""
        test_data = super().get_test_data(*args, **kwargs)
        if self.export_product is not None:
            if self.db_product.retail_price is None:
                self.db_price = ""
            else:
                self.db_price = round(float(self.db_product.retail_price), 2)
            try:
                self.export_price = round(float(self.export_product.retail_price), 2)
            except ValueError:
                self.export_price = str(self.export_product.retail_price)
        return test_data

    def is_valid(self, *args, **kwargs):
        """Check a products Retail Price matches Cloud Commerce."""
        if self.export_product is None:
            return True
        return self.db_price == self.export_price

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        return (
            f'The Retail Price of Product "{self.db_product}" ("{self.db_price}") does '
            f'not match the one in Cloud Commerce ("{self.export_price}").'
        )


class ProductDateCreatedMatches(ProductObjectValidationCheck):
    """Check a products Date Created matches Cloud Commerce."""

    name = "Product Date Created does not match"
    level = Levels.ERROR

    def is_valid(self, *args, **kwargs):
        """Check a products Date Created matches Cloud Commerce."""
        if self.export_product is None:
            return True
        if self.export_product.date_created is None:
            return False
        return self.db_product.date_created == self.export_product.date_created

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        return (
            f'The Date Created of Product "{self.db_product}" '
            f'("{self.db_product.date_created}") does not match the '
            f'one in Cloud Commerce ("{self.export_product.date_created}").'
        )


class ProductGenderMatches(ProductObjectValidationCheck):
    """Check a products Date Created matches Cloud Commerce."""

    name = "Product Gender does not match"
    level = Levels.ERROR

    def is_valid(self, *args, **kwargs):
        """Check a products Gender matches Cloud Commerce."""
        if self.export_product is None:
            return True
        if self.db_product.gender is None:
            return self.export_product.gender is None
        else:
            return self.db_product.gender.name == self.export_product.gender

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        return (
            f'The Gender of Product "{self.db_product}" ("{self.db_product.gender}") '
            f'does not match the one in Cloud Commerce ("{self.export_product.gender}").'
        )


class ProductMultipackStatusMatches(ProductObjectValidationCheck):
    """Check a products Multipack status matches Cloud Commerce."""

    name = "Product Multipack status does not match"
    level = Levels.ERROR

    def is_valid(self, *args, **kwargs):
        """Check a products Multipack status matches Cloud Commerce."""
        if self.export_product is None:
            return True
        if self.db_product.multipack is True:
            return self.export_product.product_type == "SimplePack"
        else:
            return self.export_product.product_type == "Single"

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        if self.db_product.multipack:
            return (
                f'The Product "{self.db_product}" is a multipack item in the database '
                f"but not in Cloud Commerce."
            )
        else:
            return (
                f'The Product "{self.db_product}" is not a multipack item in the '
                f"database but is in Cloud Commerce."
            )


class ProductObjectProductOptionValidationCheck(ProductObjectValidationCheck):
    """Check a Product Option of a Product matches Cloud Commerce."""

    abstract = True
    product_option_name = None
    level = Levels.ERROR

    def get_test_data(self, *args, **kwargs):
        """Return dict of validation test variables."""
        test_data = super().get_test_data(*args, **kwargs)
        self.db_product_option = self.db_product.product_option_value(
            self.product_option_name
        )
        if self.export_product is not None:
            self.export_product_option = getattr(
                self.export_product, f"{self.product_option_name.lower()}_option"
            )
        return test_data

    def is_valid(self, *args, **kwargs):
        """Check a Product Option of a Product matches Cloud Commerce."""
        if self.export_product is None:
            return True
        return self.db_product_option == self.export_product_option

    def format_error_message(self, *args, **kwargs):
        """Return a string describing the failed validation."""
        return (
            f'The "{self.product_option_name}" option of Product "{self.db_product}" '
            f'("{self.db_product_option}") does not match the one in Cloud Commerce '
            f'("{self.export_product_option}").'
        )


class ProductColourOptionMatches(ProductObjectProductOptionValidationCheck):
    """Check a Products Colour matches Cloud Commerce."""

    abstract = False
    product_option_name = "Colour"
    name = "Products Colour Product Option does not match"


class ProductSizeOptionMatches(ProductObjectProductOptionValidationCheck):
    """Check a Products Size matches Cloud Commerce."""

    abstract = False
    product_option_name = "Size"
    name = "Products Size Product Option does not match"


class ProductDesignOptionMatches(ProductObjectProductOptionValidationCheck):
    """Check a Products Design matches Cloud Commerce."""

    abstract = False
    product_option_name = "Design"
    name = "Products Design Product Option does not match"


class ProductQuantityOptionMatches(ProductObjectProductOptionValidationCheck):
    """Check a Products Quantity matches Cloud Commerce."""

    abstract = False
    product_option_name = "Quantity"
    name = "Products Quantity Product Option does not match"


class ProductWeightOptionMatches(ProductObjectProductOptionValidationCheck):
    """Check a Products Weight matches Cloud Commerce."""

    abstract = False
    product_option_name = "Weight"
    name = "Products Weight Product Option does not match"


class ProductShapeOptionMatches(ProductObjectProductOptionValidationCheck):
    """Check a Products Shape matches Cloud Commerce."""

    abstract = False
    product_option_name = "Shape"
    name = "Products Shape Product Option does not match"


class ProductStrengthOptionMatches(ProductObjectProductOptionValidationCheck):
    """Check a Products Strength matches Cloud Commerce."""

    abstract = False
    product_option_name = "Strength"
    name = "Products Strength Product Option does not match"


class ProductCalibreOptionMatches(ProductObjectProductOptionValidationCheck):
    """Check a Products Calibre matches Cloud Commerce."""

    abstract = False
    product_option_name = "Calibre"
    name = "Products Calibre Product Option does not match"


class ProductScentOptionMatches(ProductObjectProductOptionValidationCheck):
    """Check a Products Scent matches Cloud Commerce."""

    abstract = False
    product_option_name = "Scent"
    name = "Products Scent Product Option does not match"


class ProductNameOptionMatches(ProductObjectProductOptionValidationCheck):
    """Check a Products Name matches Cloud Commerce."""

    abstract = False
    product_option_name = "Name"
    name = "Products Name Product Option does not match"


class ProductExtrasOptionMatches(ProductObjectProductOptionValidationCheck):
    """Check a Products Extras matches Cloud Commerce."""

    abstract = False
    product_option_name = "Extras"
    name = "Products Extras Product Option does not match"


class ProductFinishOptionMatches(ProductObjectProductOptionValidationCheck):
    """Check a Products Finish matches Cloud Commerce."""

    abstract = False
    product_option_name = "Finish"
    name = "Products Finish Product Option does not match"


class ProductWordOptionMatches(ProductObjectProductOptionValidationCheck):
    """Check a Products Word matches Cloud Commerce."""

    abstract = False
    product_option_name = "Word"
    name = "Products Word Product Option does not match"


class ProductModelOptionMatches(ProductObjectProductOptionValidationCheck):
    """Check a Products Model matches Cloud Commerce."""

    abstract = False
    product_option_name = "Model"
    name = "Products Model Product Option does not match"


class ProductMaterialOptionMatches(ProductObjectProductOptionValidationCheck):
    """Check a Products Material matches Cloud Commerce."""

    abstract = False
    product_option_name = "Material"
    name = "Products Material Product Option does not match"
