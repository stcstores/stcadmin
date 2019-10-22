from inventory import models


class ProductRequirementsFixture:
    fixtures = ("inventory/product_requirements",)

    def setUp(self):
        self.department = models.Department.objects.get(id=1)
        self.supplier = models.Supplier.objects.get(id=1)
        self.brand = models.Brand.objects.get(id=1)
        self.manufacturer = models.Manufacturer.objects.get(id=1)
        self.package_type = models.PackageType.objects.get(id=1)
        self.international_shipping = models.InternationalShipping.objects.get(id=1)
        self.gender = models.Gender.objects.get(id=1)
        self.VAT_rate = models.VATRate.objects.get(id=1)
        self.size_product_option = models.ProductOption.objects.get(id=1)
        self.colour_product_option = models.ProductOption.objects.get(id=2)
        self.model_product_option = models.ProductOption.objects.get(id=3)
        self.red_product_option_value = models.ProductOptionValue.objects.get(id=1)
        self.green_product_option_value = models.ProductOptionValue.objects.get(id=2)
        self.blue_product_option_value = models.ProductOptionValue.objects.get(id=3)
        self.small_product_option_value = models.ProductOptionValue.objects.get(id=4)
        self.medium_product_option_value = models.ProductOptionValue.objects.get(id=5)
        self.large_product_option_value = models.ProductOptionValue.objects.get(id=6)
        self.model_product_option_value = models.ProductOptionValue.objects.get(id=7)


class SingleProductRangeFixture(ProductRequirementsFixture):
    fixtures = ProductRequirementsFixture.fixtures + ("inventory/single_product_range",)

    def setUp(self):
        super().setUp()
        self.product_range = models.ProductRange.objects.get(pk=1)
        self.product = models.Product.objects.get(id=1)


class VariationProductRangeFixture(ProductRequirementsFixture):
    fixtures = ProductRequirementsFixture.fixtures + (
        "inventory/variation_product_range",
    )

    def setUp(self):
        ProductRequirementsFixture.setUp(self)
        self.product_range = models.ProductRange.objects.get(pk=1)
        self.product = models.Product.objects.get(id=1)
        self.variations = models.Product.objects.all()


class EditingProductFixture(VariationProductRangeFixture):

    fixtures = VariationProductRangeFixture.fixtures + ("inventory/product_edit",)

    def setUp(self):
        VariationProductRangeFixture.setUp(self)
        self.product_edit = models.ProductEdit.objects.get(id=1)
        self.original_range = models.ProductRange.objects.get(id=1)
        self.product_range = models.PartialProductRange.objects.get(id=1)
        self.product = models.PartialProduct.objects.get(id=1)
        self.variations = models.PartialProduct.objects.all()


class MultipleRangesFixture(ProductRequirementsFixture):
    fixtures = ProductRequirementsFixture.fixtures + ("inventory/product_search",)

    def setUp(self):
        super().setUp()
        self.normal_range = models.ProductRange.objects.get(id=1)
        self.eol_range = models.ProductRange.objects.get(id=2)
        self.hidden_range = models.ProductRange.objects.get(id=3)

        self.normal_product = models.Product.objects.get(id=1)
        self.eol_product = models.Product.objects.get(id=2)
        self.hidden_product = models.Product.objects.get(id=3)


class UnsavedNewProductRangeFixture(ProductRequirementsFixture):
    fixtures = ProductRequirementsFixture.fixtures + ("inventory/save_edit",)

    def setUp(self):
        super().setUp()
        self.product_edit = models.ProductEdit.objects.get(id=1)
        self.product_range = models.PartialProductRange.objects.get(id=1)
