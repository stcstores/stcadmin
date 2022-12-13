import datetime as dt
from decimal import Decimal

import pytest
from django.db.utils import IntegrityError

from inventory import models


@pytest.fixture
def product(product_factory):
    return product_factory.create()


@pytest.fixture
def variant(
    product_factory,
    variation_option_value_factory,
    listing_attribute_value_factory,
):
    product = product_factory.create(
        product_range__name="Variation Product", sku="AAA-BBB-CCC"
    )
    variation_option_value_factory.create(
        product=product, variation_option__name="Colour", value="Green"
    )
    variation_option_value_factory.create(
        product=product, variation_option__name="Size", value="Medium"
    )
    listing_attribute_value_factory.create(
        product=product, listing_attribute__name="Shape", value="Round"
    )
    listing_attribute_value_factory.create(
        product=product, listing_attribute__name="Design", value="Cat"
    )
    return product


@pytest.fixture
def new_product(
    product_range_factory,
    supplier_factory,
    package_type_factory,
    vat_rate_factory,
    brand_factory,
    manufacturer_factory,
):
    product = models.Product(
        sku="AAA-BBB-CCC",
        supplier=supplier_factory.create(),
        product_range=product_range_factory.create(),
        package_type=package_type_factory.create(),
        purchase_price=8.50,
        vat_rate=vat_rate_factory.create(),
        brand=brand_factory.create(),
        manufacturer=manufacturer_factory.create(),
        weight_grams=50,
        hs_code="135487578",
    )
    product.save()
    return product


@pytest.mark.django_db
def test_product_factory_validation(product):
    product.full_clean()


@pytest.mark.django_db
def test_product_has_product_range_attribute(product):
    assert isinstance(product.product_range, models.ProductRange)


@pytest.mark.django_db
def test_product_has_sku_attribute(product):
    assert isinstance(product.sku, str)
    assert len(product.sku) > 0


@pytest.mark.django_db
def test_sku_cannot_be_null(product_factory):
    with pytest.raises(IntegrityError):
        product_factory.create(sku=None)


@pytest.mark.django_db
def test_sku_cannot_be_duplicated(product_factory):
    sku = "AAA-BBB-CCC"
    product_factory.create(sku=sku)
    with pytest.raises(IntegrityError):
        product_factory.create(sku=sku)


@pytest.mark.django_db
def test_has_retail_price_attribute(product):
    assert isinstance(product.retail_price, Decimal)


@pytest.mark.django_db
def test_retail_price_can_be_null(product_factory):
    product = product_factory.create(retail_price=None)
    product.full_clean()
    assert product.retail_price is None


@pytest.mark.django_db
def test_has_supplier_attribute(product):
    assert isinstance(product.supplier, models.Supplier)


@pytest.mark.django_db
def test_supplier_cannot_be_null(product_factory):
    with pytest.raises(IntegrityError):
        product_factory.create(supplier=None)


@pytest.mark.django_db
def test_has_supplier_sku_attribute(product):
    assert isinstance(product.supplier_sku, str)
    assert len(product.supplier_sku) > 0


@pytest.mark.django_db
def test_supplier_sku_can_be_null(product_factory):
    product = product_factory.create(supplier_sku=None)
    product.full_clean()
    assert product.supplier_sku is None


@pytest.mark.django_db
def test_has_supplier_barcode_attribute(product):
    assert isinstance(product.supplier_barcode, str)
    assert len(product.supplier_barcode) > 0


@pytest.mark.django_db
def test_supplier_barcode_can_be_null(product_factory):
    product = product_factory.create(supplier_barcode=None)
    product.full_clean()
    assert product.supplier_barcode is None


@pytest.mark.django_db
def test_has_package_type_attribute(product):
    assert isinstance(product.package_type, models.PackageType)


@pytest.mark.django_db
def test_package_type_cannot_be_null(product_factory):
    with pytest.raises(IntegrityError):
        product_factory.create(package_type=None)


@pytest.mark.django_db
def test_has_width_attribute(product):
    assert isinstance(product.width, int)


@pytest.mark.django_db
def test_width_defaults_to_zero(new_product):
    assert new_product.width == 0


@pytest.mark.django_db
def test_has_height_attribute(product):
    assert isinstance(product.height, int)


@pytest.mark.django_db
def test_height_defaults_to_zero(new_product):
    assert new_product.height == 0


@pytest.mark.django_db
def test_has_depth_attribute(product):
    assert isinstance(product.depth, int)


@pytest.mark.django_db
def test_depth_defaults_to_zero(new_product):
    assert new_product.depth == 0


@pytest.mark.django_db
def test_has_is_end_of_line_attribute(product):
    assert isinstance(product.is_end_of_line, bool)


@pytest.mark.django_db
def test_is_end_of_line_defaults_to_false(new_product):
    assert new_product.is_end_of_line is False


@pytest.mark.django_db
def test_has_created_at_attribute(product):
    assert isinstance(product.created_at, dt.datetime)


@pytest.mark.django_db
def test_has_modified_at_attribute(product):
    assert isinstance(product.modified_at, dt.datetime)


@pytest.mark.django_db
def test_has_range_order_attribute(product):
    assert isinstance(product.range_order, int)


@pytest.mark.django_db
def test_range_order_defaults_to_zero(new_product):
    assert new_product.range_order == 0


@pytest.fixture
def image(product_image_factory):
    return product_image_factory.create()


@pytest.mark.django_db
def test_has_images_attribute(product, image):
    product.images.add(image)
    assert image in product.images.all()


@pytest.mark.django_db
def test_images_uses_through_model(product, image):
    product.images.add(image)
    assert models.ProductImageLink.objects.filter(product=product, image=image).exists()


@pytest.mark.django_db
def test_has_purchase_price_attribute(product):
    assert isinstance(product.purchase_price, float)


@pytest.mark.django_db
def test_purchase_price_cannot_be_null(product_factory):
    with pytest.raises(IntegrityError):
        product_factory.create(purchase_price=None)


@pytest.mark.django_db
def test_has_vat_rate_attribute(product):
    assert isinstance(product.vat_rate, models.VATRate)


@pytest.mark.django_db
def test_vat_rate_cannot_be_null(product_factory):
    with pytest.raises(IntegrityError):
        product_factory.create(vat_rate=None)


@pytest.mark.django_db
def test_has_brand_attribute(product):
    assert isinstance(product.brand, models.Brand)


@pytest.mark.django_db
def test_brand_cannot_be_null(product_factory):
    with pytest.raises(IntegrityError):
        product_factory.create(brand=None)


@pytest.mark.django_db
def test_has_manufacturer_attribute(product):
    assert isinstance(product.manufacturer, models.Manufacturer)


@pytest.mark.django_db
def test_manufacturer_cannot_be_null(product_factory):
    with pytest.raises(IntegrityError):
        product_factory.create(manufacturer=None)


@pytest.mark.django_db
def test_has_weight_grams_attribute(product):
    assert isinstance(product.weight_grams, int)


@pytest.mark.django_db
def test_weight_grams_cannot_be_null(product_factory):
    with pytest.raises(IntegrityError):
        product_factory.create(weight_grams=None)


@pytest.mark.django_db
def test_has_hs_code_attribute(product):
    assert isinstance(product.hs_code, str)
    assert len(product.hs_code) > 0


@pytest.mark.django_db
def test_hs_code_cannot_be_null(product_factory):
    with pytest.raises(IntegrityError):
        product_factory.create(hs_code=None)


@pytest.mark.django_db
def test_name_method(product):
    assert product.name() == product.product_range.name


@pytest.mark.django_db
def test_variation_method(variant):
    expected = {"Colour": "Green", "Size": "Medium"}
    assert variant.variation() == expected


@pytest.mark.django_db
def test_listing_attributes_method(variant):
    expected = {"Design": "Cat", "Shape": "Round"}
    assert variant.listing_attributes() == expected


@pytest.mark.django_db
def test_attributes_method(variant):
    expected = {"Colour": "Green", "Size": "Medium", "Design": "Cat", "Shape": "Round"}
    assert variant.attributes() == expected


@pytest.mark.django_db
def test_variable_options_method(variant):
    assert variant.variable_options() == ["Colour", "Size"]


@pytest.mark.django_db
def test_variation_values_method(variant):
    assert variant.variation_values() == ["Green", "Medium"]


@pytest.mark.django_db
def test_name_extensions_with_supplier_sku(variant):
    assert variant.name_extensions() == ["Green", "Medium", variant.supplier_sku]


@pytest.mark.django_db
def test_name_extensions_without_supplier_sku(variant):
    variant.supplier_sku = None
    assert variant.name_extensions() == ["Green", "Medium"]


@pytest.mark.django_db
def test_full_name_property(variant):
    expected = "Variation Product - " + " - ".join(variant.name_extensions())
    assert variant.full_name == expected


@pytest.mark.django_db
def test_str_method(variant):
    assert str(variant) == "AAA-BBB-CCC: " + variant.full_name


@pytest.mark.django_db
def test_range_sku_property(product):
    assert product.range_sku == product.product_range.sku


@pytest.mark.django_db
def test_get_absolute_url_method(product):
    assert product.get_absolute_url() == f"/inventory/product/{product.pk}/"


class TestGetPrimaryImageMethod:
    @pytest.fixture
    def range_images(self, product, product_range_image_link_factory):
        images = [
            product_range_image_link_factory.create(
                product_range=product.product_range, position=i
            )
            for i in range(3)
        ]
        return images

    @pytest.fixture
    def product_images(self, product, product_image_link_factory):
        images = [
            product_image_link_factory.create(product=product, position=i)
            for i in range(3)
        ]
        return images

    @pytest.mark.django_db
    def test_returns_none_when_there_are_no_images(self, product):
        assert product.get_primary_image() is None

    @pytest.mark.django_db
    def test_returns_first_product_image(self, product, product_images, range_images):
        assert product.get_primary_image() == product_images[0].image

    @pytest.mark.django_db
    def test_returns_range_image_if_no_product_image_exists(
        self, product, range_images
    ):
        assert product.get_primary_image() == range_images[0].image
