import datetime as dt
from decimal import Decimal

import pytest
from django.db.utils import IntegrityError

from inventory import models


@pytest.fixture
def combination_product(combination_product_factory):
    return combination_product_factory.create()


@pytest.fixture
def variant(
    combination_product_factory,
    variation_option_value_factory,
    listing_attribute_value_factory,
):
    combination_product = combination_product_factory.create(
        product_range__name="Variation Product", sku="AAA-BBB-CCC"
    )
    variation_option_value_factory.create(
        product=combination_product, variation_option__name="Colour", value="Green"
    )
    variation_option_value_factory.create(
        product=combination_product, variation_option__name="Size", value="Medium"
    )
    listing_attribute_value_factory.create(
        product=combination_product, listing_attribute__name="Shape", value="Round"
    )
    listing_attribute_value_factory.create(
        product=combination_product, listing_attribute__name="Design", value="Cat"
    )
    return combination_product


@pytest.fixture
def new_combination_product(
    product_range_factory,
    supplier_factory,
    package_type_factory,
):
    combination_product = models.CombinationProduct(
        sku="AAA-BBB-CCC",
        supplier=supplier_factory.create(),
        product_range=product_range_factory.create(),
        package_type=package_type_factory.create(),
    )
    combination_product.save()
    return combination_product


@pytest.mark.django_db
def test_combination_product_factory_validation(combination_product):
    combination_product.full_clean()


@pytest.mark.django_db
def test_product_has_product_range_attribute(combination_product):
    assert isinstance(combination_product.product_range, models.ProductRange)


@pytest.mark.django_db
def test_product_has_sku_attribute(combination_product):
    assert isinstance(combination_product.sku, str)
    assert len(combination_product.sku) > 0


@pytest.mark.django_db
def test_sku_cannot_be_null(combination_product_factory):
    with pytest.raises(IntegrityError):
        combination_product_factory.create(sku=None)


@pytest.mark.django_db
def test_sku_cannot_be_duplicated(combination_product_factory):
    sku = "AAA-BBB-CCC"
    combination_product_factory.create(sku=sku)
    with pytest.raises(IntegrityError):
        combination_product_factory.create(sku=sku)


@pytest.mark.django_db
def test_has_retail_price_attribute(combination_product):
    assert isinstance(combination_product.retail_price, Decimal)


@pytest.mark.django_db
def test_retail_price_can_be_null(combination_product_factory):
    combination_product = combination_product_factory.create(retail_price=None)
    combination_product.full_clean()
    assert combination_product.retail_price is None


@pytest.mark.django_db
def test_has_supplier_attribute(combination_product):
    assert isinstance(combination_product.supplier, models.Supplier)


@pytest.mark.django_db
def test_supplier_cannot_be_null(combination_product_factory):
    with pytest.raises(IntegrityError):
        combination_product_factory.create(supplier=None)


@pytest.mark.django_db
def test_has_supplier_sku_attribute(combination_product):
    assert isinstance(combination_product.supplier_sku, str)
    assert len(combination_product.supplier_sku) > 0


@pytest.mark.django_db
def test_supplier_sku_can_be_null(combination_product_factory):
    combination_product = combination_product_factory.create(supplier_sku=None)
    combination_product.full_clean()
    assert combination_product.supplier_sku is None


@pytest.mark.django_db
def test_has_supplier_barcode_attribute(combination_product):
    assert isinstance(combination_product.supplier_barcode, str)
    assert len(combination_product.supplier_barcode) > 0


@pytest.mark.django_db
def test_supplier_barcode_can_be_null(combination_product_factory):
    combination_product = combination_product_factory.create(supplier_barcode=None)
    combination_product.full_clean()
    assert combination_product.supplier_barcode is None


@pytest.mark.django_db
def test_has_package_type_attribute(combination_product):
    assert isinstance(combination_product.package_type, models.PackageType)


@pytest.mark.django_db
def test_package_type_cannot_be_null(combination_product_factory):
    with pytest.raises(IntegrityError):
        combination_product_factory.create(package_type=None)


@pytest.mark.django_db
def test_has_width_attribute(combination_product):
    assert isinstance(combination_product.width, int)


@pytest.mark.django_db
def test_width_defaults_to_zero(new_combination_product):
    assert new_combination_product.width == 0


@pytest.mark.django_db
def test_has_height_attribute(combination_product):
    assert isinstance(combination_product.height, int)


@pytest.mark.django_db
def test_height_defaults_to_zero(new_combination_product):
    assert new_combination_product.height == 0


@pytest.mark.django_db
def test_has_depth_attribute(combination_product):
    assert isinstance(combination_product.depth, int)


@pytest.mark.django_db
def test_depth_defaults_to_zero(new_combination_product):
    assert new_combination_product.depth == 0


@pytest.mark.django_db
def test_has_is_end_of_line_attribute(combination_product):
    assert isinstance(combination_product.is_end_of_line, bool)


@pytest.mark.django_db
def test_is_end_of_line_defaults_to_false(new_combination_product):
    assert new_combination_product.is_end_of_line is False


@pytest.mark.django_db
def test_has_created_at_attribute(combination_product):
    assert isinstance(combination_product.created_at, dt.datetime)


@pytest.mark.django_db
def test_has_modified_at_attribute(combination_product):
    assert isinstance(combination_product.modified_at, dt.datetime)


@pytest.mark.django_db
def test_has_range_order_attribute(combination_product):
    assert isinstance(combination_product.range_order, int)


@pytest.mark.django_db
def test_range_order_defaults_to_zero(new_combination_product):
    assert new_combination_product.range_order == 0


@pytest.fixture
def image(product_image_factory):
    return product_image_factory.create()


@pytest.mark.django_db
def test_has_images_attribute(combination_product, image):
    combination_product.images.add(image)
    assert image in combination_product.images.all()


@pytest.mark.django_db
def test_images_uses_through_model(combination_product, image):
    combination_product.images.add(image)
    assert models.ProductImageLink.objects.filter(
        product=combination_product, image=image
    ).exists()


@pytest.fixture
def product(product_factory):
    return product_factory.create()


@pytest.mark.django_db
def test_has_products_attribute(combination_product, product):
    models.CombinationProductLink.objects.create(
        product=product, combination_product=combination_product, quantity=5
    )
    assert product in combination_product.products.all()


@pytest.mark.django_db
def test_name_method(combination_product):
    assert combination_product.name() == combination_product.product_range.name


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
def test_range_sku_property(combination_product):
    assert combination_product.range_sku == combination_product.product_range.sku


@pytest.mark.django_db
def test_get_absolute_url_method(combination_product):
    assert (
        combination_product.get_absolute_url()
        == f"/inventory/product/{combination_product.pk}/"
    )


class TestGetPrimaryImageMethod:
    @pytest.fixture
    def range_images(self, combination_product, product_range_image_link_factory):
        images = [
            product_range_image_link_factory.create(
                product_range=combination_product.product_range, position=i
            )
            for i in range(3)
        ]
        return images

    @pytest.fixture
    def product_images(self, combination_product, product_image_link_factory):
        images = [
            product_image_link_factory.create(product=combination_product, position=i)
            for i in range(3)
        ]
        return images

    @pytest.mark.django_db
    def test_returns_none_when_there_are_no_images(self, combination_product):
        assert combination_product.get_primary_image() is None

    @pytest.mark.django_db
    def test_returns_first_product_image(
        self, combination_product, product_images, range_images
    ):
        assert combination_product.get_primary_image() == product_images[0].image

    @pytest.mark.django_db
    def test_returns_range_image_if_no_product_image_exists(
        self, combination_product, range_images
    ):
        assert combination_product.get_primary_image() == range_images[0].image


@pytest.mark.django_db
def test_product_ids_method(combination_product, combination_product_link_factory):
    links = combination_product_link_factory.create_batch(
        3, combination_product=combination_product
    )
    product_ids = combination_product._product_ids()
    assert set(product_ids) == set((link.product.id for link in links))


@pytest.mark.django_db
def test_product_bay_links_property(
    combination_product, product_bay_link_factory, combination_product_link_factory
):
    links = combination_product_link_factory.create_batch(
        3, combination_product=combination_product
    )
    bay_links = [
        product_bay_link_factory.create(product=link.product) for link in links
    ]
    returned_value = combination_product.product_bay_links
    assert set(returned_value) == set(bay_links)


@pytest.mark.django_db
def test_vat_rate_property(
    combination_product, combination_product_link_factory, vat_rate_factory
):
    greater_vat_rate = vat_rate_factory.create(percentage=50)
    lesser_vat_rate = vat_rate_factory.create(percentage=20)
    for rate in (lesser_vat_rate, greater_vat_rate):
        combination_product_link_factory.create(
            combination_product=combination_product, product__vat_rate=rate
        )
    assert combination_product.vat_rate == greater_vat_rate


@pytest.mark.django_db
def test_brand_property(combination_product, combination_product_link_factory):
    links = combination_product_link_factory.create_batch(
        3, combination_product=combination_product
    )
    assert combination_product.brand == links[0].product.brand


@pytest.mark.django_db
def test_manufacturer_property(combination_product, combination_product_link_factory):
    links = combination_product_link_factory.create_batch(
        3, combination_product=combination_product
    )
    assert combination_product.manufacturer == links[0].product.manufacturer


@pytest.mark.django_db
def test_hs_code_property(combination_product, combination_product_link_factory):
    links = combination_product_link_factory.create_batch(
        3, combination_product=combination_product
    )
    assert combination_product.hs_code == links[0].product.hs_code


@pytest.mark.django_db
def test_weight_grams_property(combination_product, combination_product_link_factory):
    links = combination_product_link_factory.create_batch(
        3, combination_product=combination_product
    )
    assert combination_product.weight_grams == sum(
        (link.product.weight_grams for link in links)
    )


@pytest.mark.django_db
def test_purchase_price_grams_property(
    combination_product, combination_product_link_factory
):
    links = combination_product_link_factory.create_batch(
        3, combination_product=combination_product
    )
    assert combination_product.purchase_price == sum(
        (link.product.purchase_price for link in links)
    )
