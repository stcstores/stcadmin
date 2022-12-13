import datetime as dt
from decimal import Decimal

import pytest
from django.db.utils import IntegrityError

from inventory import models


@pytest.fixture
def base_product(base_product_factory):
    return base_product_factory.create()


@pytest.fixture
def variant(
    base_product_factory,
    variation_option_value_factory,
    listing_attribute_value_factory,
):
    base_product = base_product_factory.create(
        product_range__name="Variation Product", sku="AAA-BBB-CCC"
    )
    variation_option_value_factory.create(
        product=base_product, variation_option__name="Colour", value="Green"
    )
    variation_option_value_factory.create(
        product=base_product, variation_option__name="Size", value="Medium"
    )
    listing_attribute_value_factory.create(
        product=base_product, listing_attribute__name="Shape", value="Round"
    )
    listing_attribute_value_factory.create(
        product=base_product, listing_attribute__name="Design", value="Cat"
    )
    return base_product


@pytest.fixture
def new_base_product(
    product_range_factory,
    supplier_factory,
    package_type_factory,
):
    base_product = models.BaseProduct(
        sku="AAA-BBB-CCC",
        supplier=supplier_factory.create(),
        product_range=product_range_factory.create(),
        package_type=package_type_factory.create(),
    )
    base_product.save()
    return base_product


@pytest.mark.django_db
def test_base_product_factory_validation(base_product):
    base_product.full_clean()


@pytest.mark.django_db
def test_product_has_product_range_attribute(base_product):
    assert isinstance(base_product.product_range, models.ProductRange)


@pytest.mark.django_db
def test_product_has_sku_attribute(base_product):
    assert isinstance(base_product.sku, str)
    assert len(base_product.sku) > 0


@pytest.mark.django_db
def test_sku_cannot_be_null(base_product_factory):
    with pytest.raises(IntegrityError):
        base_product_factory.create(sku=None)


@pytest.mark.django_db
def test_sku_cannot_be_duplicated(base_product_factory):
    sku = "AAA-BBB-CCC"
    base_product_factory.create(sku=sku)
    with pytest.raises(IntegrityError):
        base_product_factory.create(sku=sku)


@pytest.mark.django_db
def test_has_retail_price_attribute(base_product):
    assert isinstance(base_product.retail_price, Decimal)


@pytest.mark.django_db
def test_retail_price_can_be_null(base_product_factory):
    base_product = base_product_factory.create(retail_price=None)
    base_product.full_clean()
    assert base_product.retail_price is None


@pytest.mark.django_db
def test_has_supplier_attribute(base_product):
    assert isinstance(base_product.supplier, models.Supplier)


@pytest.mark.django_db
def test_supplier_cannot_be_null(base_product_factory):
    with pytest.raises(IntegrityError):
        base_product_factory.create(supplier=None)


@pytest.mark.django_db
def test_has_supplier_sku_attribute(base_product):
    assert isinstance(base_product.supplier_sku, str)
    assert len(base_product.supplier_sku) > 0


@pytest.mark.django_db
def test_supplier_sku_can_be_null(base_product_factory):
    base_product = base_product_factory.create(supplier_sku=None)
    base_product.full_clean()
    assert base_product.supplier_sku is None


@pytest.mark.django_db
def test_has_supplier_barcode_attribute(base_product):
    assert isinstance(base_product.supplier_barcode, str)
    assert len(base_product.supplier_barcode) > 0


@pytest.mark.django_db
def test_supplier_barcode_can_be_null(base_product_factory):
    base_product = base_product_factory.create(supplier_barcode=None)
    base_product.full_clean()
    assert base_product.supplier_barcode is None


@pytest.mark.django_db
def test_has_package_type_attribute(base_product):
    assert isinstance(base_product.package_type, models.PackageType)


@pytest.mark.django_db
def test_package_type_cannot_be_null(base_product_factory):
    with pytest.raises(IntegrityError):
        base_product_factory.create(package_type=None)


@pytest.mark.django_db
def test_has_width_attribute(base_product):
    assert isinstance(base_product.width, int)


@pytest.mark.django_db
def test_width_defaults_to_zero(new_base_product):
    assert new_base_product.width == 0


@pytest.mark.django_db
def test_has_height_attribute(base_product):
    assert isinstance(base_product.height, int)


@pytest.mark.django_db
def test_height_defaults_to_zero(new_base_product):
    assert new_base_product.height == 0


@pytest.mark.django_db
def test_has_depth_attribute(base_product):
    assert isinstance(base_product.depth, int)


@pytest.mark.django_db
def test_depth_defaults_to_zero(new_base_product):
    assert new_base_product.depth == 0


@pytest.mark.django_db
def test_has_is_end_of_line_attribute(base_product):
    assert isinstance(base_product.is_end_of_line, bool)


@pytest.mark.django_db
def test_is_end_of_line_defaults_to_false(new_base_product):
    assert new_base_product.is_end_of_line is False


@pytest.mark.django_db
def test_has_created_at_attribute(base_product):
    assert isinstance(base_product.created_at, dt.datetime)


@pytest.mark.django_db
def test_has_modified_at_attribute(base_product):
    assert isinstance(base_product.modified_at, dt.datetime)


@pytest.mark.django_db
def test_has_range_order_attribute(base_product):
    assert isinstance(base_product.range_order, int)


@pytest.mark.django_db
def test_range_order_defaults_to_zero(new_base_product):
    assert new_base_product.range_order == 0


@pytest.fixture
def image(product_image_factory):
    return product_image_factory.create()


@pytest.mark.django_db
def test_has_images_attribute(base_product, image):
    base_product.images.add(image)
    assert image in base_product.images.all()


@pytest.mark.django_db
def test_images_uses_through_model(base_product, image):
    base_product.images.add(image)
    assert models.ProductImageLink.objects.filter(
        product=base_product, image=image
    ).exists()


@pytest.mark.django_db
def test_name_method(base_product):
    assert base_product.name() == base_product.product_range.name


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
def test_name_extensions(variant):
    assert variant.name_extensions() == variant.variation_values()


@pytest.mark.django_db
def test_full_name_property(variant):
    assert variant.full_name == "Variation Product - Green - Medium"


@pytest.mark.django_db
def test_str_method(variant):
    assert str(variant) == "AAA-BBB-CCC: Variation Product - Green - Medium"


@pytest.mark.django_db
def test_range_sku_property(base_product):
    assert base_product.range_sku == base_product.product_range.sku


@pytest.mark.django_db
def test_get_absolute_url_method(base_product):
    assert base_product.get_absolute_url() == f"/inventory/product/{base_product.pk}/"


class TestGetPrimaryImageMethod:
    @pytest.fixture
    def range_images(self, base_product, product_range_image_link_factory):
        images = [
            product_range_image_link_factory.create(
                product_range=base_product.product_range, position=i
            )
            for i in range(3)
        ]
        return images

    @pytest.fixture
    def product_images(self, base_product, product_image_link_factory):
        images = [
            product_image_link_factory.create(product=base_product, position=i)
            for i in range(3)
        ]
        return images

    @pytest.mark.django_db
    def test_returns_none_when_there_are_no_images(self, base_product):
        assert base_product.get_primary_image() is None

    @pytest.mark.django_db
    def test_returns_first_product_image(
        self, base_product, product_images, range_images
    ):
        assert base_product.get_primary_image() == product_images[0].image

    @pytest.mark.django_db
    def test_returns_range_image_if_no_product_image_exists(
        self, base_product, range_images
    ):
        assert base_product.get_primary_image() == range_images[0].image
