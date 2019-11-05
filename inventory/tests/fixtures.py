from inventory import models


class LocationsFixture:
    fixtures = ("inventory/locations",)

    @property
    def warehouse_1(self):
        return models.Warehouse.objects.get(id=1)

    @property
    def warehouse_2(self):
        return models.Warehouse.objects.get(id=2)

    @property
    def warehouse_1_defualt_bay(self):
        return models.Bay.objects.get(id=1)

    @property
    def warehouse_2_default_bay(self):
        return models.Bay.objects.get(id=2)

    @property
    def warehouse_1_bay_1(self):
        return models.Bay.objects.get(id=3)

    @property
    def warehouse_1_bay_2(self):
        return models.Bay.objects.get(id=4)

    @property
    def warehouse_1_bay_3(self):
        return models.Bay.objects.get(id=5)

    @property
    def warehouse_1_bay_4(self):
        return models.Bay.objects.get(id=6)

    @property
    def warehouse_1_bay_5(self):
        return models.Bay.objects.get(id=7)

    @property
    def warehouse_2_bay_1(self):
        return models.Bay.objects.get(id=8)

    @property
    def warehouse_2_bay_2(self):
        return models.Bay.objects.get(id=9)

    @property
    def warehouse_2_bay_3(self):
        return models.Bay.objects.get(id=10)

    @property
    def warehouse_2_bay_4(self):
        return models.Bay.objects.get(id=11)

    @property
    def warehouse_2_bay_5(self):
        return models.Bay.objects.get(id=12)


class ProductRequirementsFixture(LocationsFixture):
    fixtures = LocationsFixture.fixtures + ("inventory/product_requirements",)

    @property
    def department(self):
        return models.Department.objects.get(id=1)

    @property
    def second_department(self):
        return models.Department.objects.get(id=2)

    @property
    def supplier(self):
        return models.Supplier.objects.get(id=1)

    @property
    def second_supplier(self):
        return models.Supplier.objects.get(id=2)

    @property
    def supplier_contact(self):
        return models.SupplierContact.objects.get(id=1)

    @property
    def brand(self):
        return models.Brand.objects.get(id=1)

    @property
    def second_brand(self):
        return models.Brand.objects.get(id=2)

    @property
    def manufacturer(self):
        return models.Manufacturer.objects.get(id=1)

    @property
    def second_manufacturer(self):
        return models.Manufacturer.objects.get(id=2)

    @property
    def package_type(self):
        return models.PackageType.objects.get(id=1)

    @property
    def second_package_type(self):
        return models.PackageType.objects.get(id=2)

    @property
    def international_shipping(self):
        return models.InternationalShipping.objects.get(id=1)

    @property
    def second_international_shipping(self):
        return models.InternationalShipping.objects.get(id=2)

    @property
    def gender(self):
        return models.Gender.objects.get(id=1)

    @property
    def second_gender(self):
        return models.Gender.objects.get(id=2)

    @property
    def VAT_rate(self):
        return models.VATRate.objects.get(id=1)

    @property
    def second_VAT_rate(self):
        return models.VATRate.objects.get(id=2)

    @property
    def size_product_option(self):
        return models.ProductOption.objects.get(id=1)

    @property
    def colour_product_option(self):
        return models.ProductOption.objects.get(id=2)

    @property
    def model_product_option(self):
        return models.ProductOption.objects.get(id=3)

    @property
    def design_product_option(self):
        return models.ProductOption.objects.get(id=4)

    @property
    def red_product_option_value(self):
        return models.ProductOptionValue.objects.get(id=1)

    @property
    def green_product_option_value(self):
        return models.ProductOptionValue.objects.get(id=2)

    @property
    def blue_product_option_value(self):
        return models.ProductOptionValue.objects.get(id=3)

    @property
    def purple_product_option_value(self):
        return models.ProductOptionValue.objects.get(id=4)

    @property
    def magenta_product_option_value(self):
        return models.ProductOptionValue.objects.get(id=5)

    @property
    def small_product_option_value(self):
        return models.ProductOptionValue.objects.get(id=6)

    @property
    def medium_product_option_value(self):
        return models.ProductOptionValue.objects.get(id=7)

    @property
    def large_product_option_value(self):
        return models.ProductOptionValue.objects.get(id=8)

    @property
    def xl_product_option_value(self):
        return models.ProductOptionValue.objects.get(id=9)

    @property
    def xxl_product_option_value(self):
        return models.ProductOptionValue.objects.get(id=10)

    @property
    def model_product_option_value(self):
        return models.ProductOptionValue.objects.get(id=11)

    @property
    def second_model_product_option_value(self):
        return models.ProductOptionValue.objects.get(id=12)

    @property
    def cat_product_option_value(self):
        return models.ProductOptionValue.objects.get(id=13)

    @property
    def dog_product_option_value(self):
        return models.ProductOptionValue.objects.get(id=14)

    @property
    def horse_product_option_value(self):
        return models.ProductOptionValue.objects.get(id=15)

    @property
    def used_product_options(self):
        return [
            self.colour_product_option,
            self.size_product_option,
            self.model_product_option,
        ]

    @property
    def all_product_options(self):
        return self.used_product_options.extend([self.design_product_option])

    @property
    def used_product_option_values(self):
        return [
            self.small_product_option_value,
            self.medium_product_option_value,
            self.large_product_option_value,
            self.red_product_option_value,
            self.green_product_option_value,
            self.blue_product_option_value,
            self.model_product_option_value,
        ]

    @property
    def all_product_option_values(self):
        return self.used_product_option_values.extend(
            [
                self.xl_product_option_value,
                self.xxl_product_option_value,
                self.purple_product_option_value,
                self.magenta_product_option_value,
                self.cat_product_option_value,
                self.dog_product_option_value,
                self.horse_product_option_value,
                self.second_model_product_option_value,
            ]
        )


class SingleProductRangeFixture(ProductRequirementsFixture):
    fixtures = ProductRequirementsFixture.fixtures + ("inventory/single_product_range",)

    @property
    def product_range(self):
        return models.ProductRange.objects.get(pk=1)

    @property
    def product(self):
        return models.Product.objects.get(id=1)


class VariationProductRangeFixture(ProductRequirementsFixture):
    fixtures = ProductRequirementsFixture.fixtures + (
        "inventory/variation_product_range",
    )

    @property
    def product_range(self):
        return models.ProductRange.objects.get(pk=1)

    @property
    def product(self):
        return self.small_red_product

    @property
    def small_red_product(self):
        return models.Product.objects.get(id=1)

    @property
    def small_green_product(self):
        return models.Product.objects.get(id=2)

    @property
    def small_blue_product(self):
        return models.Product.objects.get(id=3)

    @property
    def medium_red_product(self):
        return models.Product.objects.get(id=4)

    @property
    def medium_green_product(self):
        return models.Product.objects.get(id=5)

    @property
    def medium_blue_product(self):
        return models.Product.objects.get(id=6)

    @property
    def large_red_product(self):
        return models.Product.objects.get(id=7)

    @property
    def large_green_product(self):
        return models.Product.objects.get(id=8)

    @property
    def large_blue_product(self):
        return models.Product.objects.get(id=9)

    @property
    def variations(self):
        return models.Product.objects.all().order_by("id")


class EditingProductFixture(VariationProductRangeFixture):

    fixtures = VariationProductRangeFixture.fixtures + ("inventory/product_edit",)

    @property
    def product_edit(self):
        return models.ProductEdit.objects.get(id=1)

    @property
    def original_range(self):
        return models.ProductRange.objects.get(id=1)

    @property
    def product_range(self):
        return models.PartialProductRange.objects.get(id=1)

    @property
    def product(self):
        return self.small_red_product

    @property
    def small_red_product(self):
        return models.PartialProduct.objects.get(id=1)

    @property
    def small_green_product(self):
        return models.PartialProduct.objects.get(id=2)

    @property
    def small_blue_product(self):
        return models.PartialProduct.objects.get(id=3)

    @property
    def medium_red_product(self):
        return models.PartialProduct.objects.get(id=4)

    @property
    def medium_green_product(self):
        return models.PartialProduct.objects.get(id=5)

    @property
    def medium_blue_product(self):
        return models.PartialProduct.objects.get(id=6)

    @property
    def large_red_product(self):
        return models.PartialProduct.objects.get(id=7)

    @property
    def large_green_product(self):
        return models.PartialProduct.objects.get(id=8)

    @property
    def large_blue_product(self):
        return models.PartialProduct.objects.get(id=9)

    @property
    def variations(self):
        return models.PartialProduct.objects.all().order_by("id")


class MultipleRangesFixture(ProductRequirementsFixture):
    fixtures = ProductRequirementsFixture.fixtures + ("inventory/product_search",)

    @property
    def normal_range(self):
        return models.ProductRange.objects.get(id=1)

    @property
    def eol_range(self):
        return models.ProductRange.objects.get(id=2)

    @property
    def hidden_range(self):
        return models.ProductRange.objects.get(id=3)

    @property
    def normal_product(self):
        return models.Product.objects.get(id=1)

    @property
    def eol_product(self):
        return models.Product.objects.get(id=2)

    @property
    def hidden_product(self):
        return models.Product.objects.get(id=3)


class UnsavedNewProductRangeFixture(ProductRequirementsFixture):
    fixtures = ProductRequirementsFixture.fixtures + ("inventory/new_product",)

    @property
    def product_edit(self):
        return models.ProductEdit.objects.get(id=1)

    @property
    def product_range(self):
        return models.PartialProductRange.objects.get(id=1)
