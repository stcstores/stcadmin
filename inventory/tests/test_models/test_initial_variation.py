import datetime as dt
from decimal import Decimal

import pytest
from django.db.utils import IntegrityError

from inventory import models


@pytest.fixture
def initial_variation(initial_variation_factory):
    return initial_variation_factory.create()


@pytest.fixture
def variant(
    initial_variation_factory,
    variation_option_value_factory,
    listing_attribute_value_factory,
):
    initial_variation = initial_variation_factory.create(
        product_range__name="Variation initial_variation", sku="AAA-BBB-CCC"
    )
    variation_option_value_factory.create(
        product=initial_variation,
        variation_option__name="Colour",
        value="Green",
    )
    variation_option_value_factory.create(
        product=initial_variation,
        variation_option__name="Size",
        value="Medium",
    )
    listing_attribute_value_factory.create(
        product=initial_variation,
        listing_attribute__name="Shape",
        value="Round",
    )
    listing_attribute_value_factory.create(
        product=initial_variation,
        listing_attribute__name="Design",
        value="Cat",
    )
    return initial_variation


@pytest.fixture
def new_initial_variation(
    product_range_factory,
    supplier_factory,
    package_type_factory,
    vat_rate_factory,
    brand_factory,
    manufacturer_factory,
):
    initial_variation = models.InitialVariation(
        sku="AAA-BBB-CCC",
        supplier=supplier_factory.create(),
        product_range=product_range_factory.create(),
        package_type=package_type_factory.create(),
        purchase_price=Decimal("8.50"),
        vat_rate=vat_rate_factory.create(),
        brand=brand_factory.create(),
        manufacturer=manufacturer_factory.create(),
        weight_grams=50,
        hs_code="135487578",
    )
    initial_variation.save()
    return initial_variation


@pytest.mark.django_db
def test_initial_variation_factory_validation(initial_variation):
    initial_variation.full_clean()


@pytest.mark.django_db
def test_initial_variation_has_product_range_attribute(initial_variation):
    assert isinstance(initial_variation.product_range, models.ProductRange)


@pytest.mark.django_db
def test_initial_variation_has_sku_attribute(initial_variation):
    assert isinstance(initial_variation.sku, str)
    assert len(initial_variation.sku) > 0


@pytest.mark.django_db
def test_sku_cannot_be_null(initial_variation_factory):
    with pytest.raises(IntegrityError):
        initial_variation_factory.create(sku=None)


@pytest.mark.django_db
def test_sku_cannot_be_duplicated(initial_variation_factory):
    sku = "AAA-BBB-CCC"
    initial_variation_factory.create(sku=sku)
    with pytest.raises(IntegrityError):
        initial_variation_factory.create(sku=sku)


@pytest.mark.django_db
def test_has_retail_price_attribute(initial_variation):
    assert isinstance(initial_variation.retail_price, Decimal)


@pytest.mark.django_db
def test_retail_price_can_be_null(initial_variation_factory):
    initial_variation = initial_variation_factory.create(retail_price=None)
    initial_variation.full_clean()
    assert initial_variation.retail_price is None


@pytest.mark.django_db
def test_has_supplier_attribute(initial_variation):
    assert isinstance(initial_variation.supplier, models.Supplier)


@pytest.mark.django_db
def test_supplier_cannot_be_null(initial_variation_factory):
    with pytest.raises(IntegrityError):
        initial_variation_factory.create(supplier=None)


@pytest.mark.django_db
def test_has_supplier_sku_attribute(initial_variation):
    assert isinstance(initial_variation.supplier_sku, str)
    assert len(initial_variation.supplier_sku) > 0


@pytest.mark.django_db
def test_supplier_sku_can_be_null(initial_variation_factory):
    initial_variation = initial_variation_factory.create(supplier_sku=None)
    initial_variation.full_clean()
    assert initial_variation.supplier_sku is None


@pytest.mark.django_db
def test_has_supplier_barcode_attribute(initial_variation):
    assert isinstance(initial_variation.supplier_barcode, str)
    assert len(initial_variation.supplier_barcode) > 0


@pytest.mark.django_db
def test_supplier_barcode_can_be_null(initial_variation_factory):
    initial_variation = initial_variation_factory.create(supplier_barcode=None)
    initial_variation.full_clean()
    assert initial_variation.supplier_barcode is None


@pytest.mark.django_db
def test_has_package_type_attribute(initial_variation):
    assert isinstance(initial_variation.package_type, models.PackageType)


@pytest.mark.django_db
def test_package_type_cannot_be_null(initial_variation_factory):
    with pytest.raises(IntegrityError):
        initial_variation_factory.create(package_type=None)


@pytest.mark.django_db
def test_has_width_attribute(initial_variation):
    assert isinstance(initial_variation.width, int)


@pytest.mark.django_db
def test_width_defaults_to_zero(new_initial_variation):
    assert new_initial_variation.width == 0


@pytest.mark.django_db
def test_has_height_attribute(initial_variation):
    assert isinstance(initial_variation.height, int)


@pytest.mark.django_db
def test_height_defaults_to_zero(new_initial_variation):
    assert new_initial_variation.height == 0


@pytest.mark.django_db
def test_has_depth_attribute(initial_variation):
    assert isinstance(initial_variation.depth, int)


@pytest.mark.django_db
def test_depth_defaults_to_zero(new_initial_variation):
    assert new_initial_variation.depth == 0


@pytest.mark.django_db
def test_has_is_end_of_line_attribute(initial_variation):
    assert isinstance(initial_variation.is_end_of_line, bool)


@pytest.mark.django_db
def test_is_end_of_line_defaults_to_false(new_initial_variation):
    assert new_initial_variation.is_end_of_line is False


@pytest.mark.django_db
def test_has_created_at_attribute(initial_variation):
    assert isinstance(initial_variation.created_at, dt.datetime)


@pytest.mark.django_db
def test_has_modified_at_attribute(initial_variation):
    assert isinstance(initial_variation.modified_at, dt.datetime)


@pytest.mark.django_db
def test_has_range_order_attribute(initial_variation):
    assert isinstance(initial_variation.range_order, int)


@pytest.mark.django_db
def test_range_order_defaults_to_zero(new_initial_variation):
    assert new_initial_variation.range_order == 0


@pytest.fixture
def image(product_image_factory):
    return product_image_factory.create()


@pytest.mark.django_db
def test_has_images_attribute(initial_variation, image):
    initial_variation.images.add(image)
    assert image in initial_variation.images.all()


@pytest.mark.django_db
def test_images_uses_through_model(initial_variation, image):
    initial_variation.images.add(image)
    assert models.ProductImageLink.objects.filter(
        product=initial_variation, image=image
    ).exists()


@pytest.mark.django_db
def test_has_purchase_price_attribute(initial_variation):
    assert isinstance(initial_variation.purchase_price, Decimal)


@pytest.mark.django_db
def test_purchase_price_cannot_be_null(initial_variation_factory):
    with pytest.raises(IntegrityError):
        initial_variation_factory.create(purchase_price=None)


@pytest.mark.django_db
def test_has_vat_rate_attribute(initial_variation):
    assert isinstance(initial_variation.vat_rate, models.VATRate)


@pytest.mark.django_db
def test_vat_rate_cannot_be_null(initial_variation_factory):
    with pytest.raises(IntegrityError):
        initial_variation_factory.create(vat_rate=None)


@pytest.mark.django_db
def test_has_brand_attribute(initial_variation):
    assert isinstance(initial_variation.brand, models.Brand)


@pytest.mark.django_db
def test_brand_cannot_be_null(initial_variation_factory):
    with pytest.raises(IntegrityError):
        initial_variation_factory.create(brand=None)


@pytest.mark.django_db
def test_has_manufacturer_attribute(initial_variation):
    assert isinstance(initial_variation.manufacturer, models.Manufacturer)


@pytest.mark.django_db
def test_manufacturer_cannot_be_null(initial_variation_factory):
    with pytest.raises(IntegrityError):
        initial_variation_factory.create(manufacturer=None)


@pytest.mark.django_db
def test_has_weight_grams_attribute(initial_variation):
    assert isinstance(initial_variation.weight_grams, int)


@pytest.mark.django_db
def test_weight_grams_cannot_be_null(initial_variation_factory):
    with pytest.raises(IntegrityError):
        initial_variation_factory.create(weight_grams=None)


@pytest.mark.django_db
def test_has_hs_code_attribute(initial_variation):
    assert isinstance(initial_variation.hs_code, str)
    assert len(initial_variation.hs_code) > 0


@pytest.mark.django_db
def test_hs_code_cannot_be_null(initial_variation_factory):
    with pytest.raises(IntegrityError):
        initial_variation_factory.create(hs_code=None)


@pytest.mark.django_db
def test_name_method(initial_variation):
    assert initial_variation.name() == initial_variation.product_range.name


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
    expected = "Variation initial_variation - " + " - ".join(variant.name_extensions())
    assert variant.full_name == expected


@pytest.mark.django_db
def test_str_method(variant):
    assert str(variant) == "AAA-BBB-CCC: " + variant.full_name


@pytest.mark.django_db
def test_range_sku_property(initial_variation):
    assert initial_variation.range_sku == initial_variation.product_range.sku


@pytest.mark.django_db
def test_get_absolute_url_method(initial_variation):
    assert (
        initial_variation.get_absolute_url()
        == f"/inventory/product/{initial_variation.pk}/"
    )


class TestGetPrimaryImageMethod:
    @pytest.fixture
    def range_images(self, initial_variation, product_range_image_link_factory):
        images = [
            product_range_image_link_factory.create(
                product_range=initial_variation.product_range,
                position=i,
            )
            for i in range(3)
        ]
        return images

    @pytest.fixture
    def product_images(self, initial_variation, product_image_link_factory):
        images = [
            product_image_link_factory.create(product=initial_variation, position=i)
            for i in range(3)
        ]
        return images

    @pytest.mark.django_db
    def test_returns_none_when_there_are_no_images(self, initial_variation):
        assert initial_variation.get_primary_image() is None

    @pytest.mark.django_db
    def test_returns_first_initial_variation_image(
        self, initial_variation, product_images, range_images
    ):
        assert initial_variation.get_primary_image() == product_images[0].image

    @pytest.mark.django_db
    def test_returns_range_image_if_no_initial_variation_image_exists(
        self, initial_variation, range_images
    ):
        assert initial_variation.get_primary_image() == range_images[0].image


@pytest.fixture
def variation_options(variation_option_factory):
    variation_option_factory.create(name="Colour")
    variation_option_factory.create(name="Size")


class TestCreateVariationMethod:
    @pytest.fixture
    def created_variation(self, variation_options, initial_variation):
        return initial_variation._create_variation({"Colour": "Red", "Size": "Large"})

    @pytest.mark.django_db
    def test_sets_sku(self, initial_variation, created_variation):
        assert isinstance(created_variation.sku, str)
        assert len(created_variation.sku) > 0
        assert created_variation.sku != initial_variation.sku

    @pytest.mark.django_db
    def test_sets_product_range(self, created_variation, initial_variation):
        assert created_variation.product_range == initial_variation.product_range

    @pytest.mark.django_db
    def test_sets_retail_price(self, created_variation, initial_variation):
        assert created_variation.retail_price == initial_variation.retail_price

    @pytest.mark.django_db
    def test_sets_supplier(self, created_variation, initial_variation):
        assert created_variation.supplier == initial_variation.supplier

    @pytest.mark.django_db
    def test_sets_supplier_sku(self, created_variation, initial_variation):
        assert created_variation.supplier_sku == initial_variation.supplier_sku

    @pytest.mark.django_db
    def test_sets_barcode(self, created_variation, initial_variation):
        assert created_variation.barcode == initial_variation.barcode

    @pytest.mark.django_db
    def test_sets_supplier_barcode(self, created_variation, initial_variation):
        assert created_variation.supplier_barcode == initial_variation.supplier_barcode

    @pytest.mark.django_db
    def test_sets_package_type(self, created_variation, initial_variation):
        assert created_variation.package_type == initial_variation.package_type

    @pytest.mark.django_db
    def test_sets_width(self, created_variation, initial_variation):
        assert created_variation.width == initial_variation.width

    @pytest.mark.django_db
    def test_sets_height(self, created_variation, initial_variation):
        assert created_variation.height == initial_variation.height

    @pytest.mark.django_db
    def test_sets_depth(self, created_variation, initial_variation):
        assert created_variation.depth == initial_variation.depth

    @pytest.mark.django_db
    def test_sets_is_end_of_line(self, created_variation, initial_variation):
        assert created_variation.is_end_of_line == initial_variation.is_end_of_line

    @pytest.mark.django_db
    def test_sets_range_order(self, created_variation, initial_variation):
        assert created_variation.range_order == initial_variation.range_order

    @pytest.mark.django_db
    def test_sets_purchase_price(self, created_variation, initial_variation):
        assert created_variation.purchase_price == initial_variation.purchase_price

    @pytest.mark.django_db
    def test_sets_vat_rate(self, created_variation, initial_variation):
        assert created_variation.vat_rate == initial_variation.vat_rate

    @pytest.mark.django_db
    def test_sets_brand(self, created_variation, initial_variation):
        assert created_variation.brand == initial_variation.brand

    @pytest.mark.django_db
    def test_sets_manufacturer(self, created_variation, initial_variation):
        assert created_variation.manufacturer == initial_variation.manufacturer

    @pytest.mark.django_db
    def test_sets_weight_grams(self, created_variation, initial_variation):
        assert created_variation.weight_grams == initial_variation.weight_grams

    @pytest.mark.django_db
    def test_sets_hs_code(self, created_variation, initial_variation):
        assert created_variation.hs_code == initial_variation.hs_code


@pytest.mark.django_db
def test_create_variations_method(variation_options, initial_variation):
    variations = [
        {"Colour": "Red", "Size": "Small"},
        {"Colour": "Blue", "Size": "Medium"},
    ]
    created_variations = initial_variation.create_variations(variations)
    assert len(created_variations) == 2
    assert models.VariationOptionValue.objects.filter(
        product=created_variations[0], variation_option__name="Colour", value="Red"
    ).exists()
    assert models.VariationOptionValue.objects.filter(
        product=created_variations[0], variation_option__name="Size", value="Small"
    ).exists()
    assert models.VariationOptionValue.objects.filter(
        product=created_variations[1], variation_option__name="Colour", value="Blue"
    ).exists()
    assert models.VariationOptionValue.objects.filter(
        product=created_variations[1], variation_option__name="Size", value="Medium"
    ).exists()
