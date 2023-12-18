import datetime as dt
import itertools

import pytest
from django.contrib.auth import get_user_model

from inventory import models


@pytest.fixture
def product_range(product_range_factory):
    product_range = product_range_factory.create()
    product_range.full_clean()
    return product_range


@pytest.fixture
def variation_range(
    variation_option_factory,
    variation_option_value_factory,
    listing_attribute_factory,
    listing_attribute_value_factory,
    product_factory,
    product_range,
):
    product_range = product_range
    colour = variation_option_factory(name="Colour")
    size = variation_option_factory(name="Size")
    design = listing_attribute_factory(name="Design")
    quantity = listing_attribute_factory(name="Quantity")
    variations = itertools.product(
        ("Red", "Green", "Blue"), ("Small", "Medium", "Large")
    )
    for colour_value, size_value in variations:
        product = product_factory.create(product_range=product_range)
        variation_option_value_factory.create(
            product=product, variation_option=colour, value=colour_value
        )
        variation_option_value_factory.create(
            product=product, variation_option=size, value=size_value
        )
        listing_attribute_value_factory.create(
            product=product, listing_attribute=design, value="Rectangular"
        )
        listing_attribute_value_factory.create(
            product=product, listing_attribute=quantity, value="5"
        )
    return product_range


@pytest.mark.django_db
def test_has_name_attribute(product_range):
    assert isinstance(product_range.name, str)
    assert len(product_range.name) > 0


@pytest.mark.django_db
def test_has_status_attribute(product_range):
    assert isinstance(product_range.status, str)
    assert len(product_range.status) > 0


@pytest.mark.django_db
def test_has_description_attribute(product_range):
    assert isinstance(product_range.description, str)
    assert len(product_range.description) > 0


@pytest.mark.django_db
def test_has_search_terms_attribute(product_range):
    assert isinstance(product_range.search_terms, list)


@pytest.mark.django_db
def test_has_bullet_points_attribute(product_range):
    assert isinstance(product_range.bullet_points, list)


@pytest.mark.django_db
def test_has_managed_by_attribute(product_range):
    assert isinstance(product_range.managed_by, get_user_model())


@pytest.mark.django_db
def test_has_created_at_attribute(product_range):
    assert isinstance(product_range.created_at, dt.datetime)


@pytest.mark.django_db
def test_has_modified_at_attribute(product_range):
    assert isinstance(product_range.modified_at, dt.datetime)


@pytest.mark.django_db
def test_str_method(product_range_factory):
    product_range = product_range_factory(sku="RNG_AAA-BBB-CCC", name="Test Range")
    assert str(product_range) == "RNG_AAA-BBB-CCC: Test Range"


@pytest.mark.django_db
def test_get_absolute_url_method(product_range):
    assert isinstance(product_range.get_absolute_url(), str)


@pytest.mark.django_db
def test_complete_new_range_method(user_factory, product_range_factory):
    user = user_factory.create()
    product_range = product_range_factory(status=models.ProductRange.CREATING)
    product_range.complete_new_range(user)
    product_range.refresh_from_db()
    assert product_range.status == models.ProductRange.COMPLETE


@pytest.mark.django_db
def test_complete_new_range_method_sets_product_barcodes(
    user_factory, product_range_factory, product_factory, barcode_factory
):
    barcode_factory.create_batch(5, used=False)
    user = user_factory.create()
    product_range = product_range_factory(status=models.ProductRange.CREATING)
    products = product_factory.create_batch(
        5, product_range=product_range, barcode=None
    )
    product_range.complete_new_range(user)
    for product in products:
        product.refresh_from_db()
        assert product.barcode is not None
        barcode = models.Barcode.objects.get(barcode=product.barcode)
        assert product.barcode == barcode.barcode
        assert barcode.used_by == user
        assert barcode.used_for == product.sku


@pytest.mark.django_db
def test_complete_new_range_method_does_not_replace_set_product_barcodes(
    user_factory, product_range_factory, product_factory
):
    barcode = "641975941243"
    user = user_factory.create()
    product_range = product_range_factory(status=models.ProductRange.CREATING)
    product = product_factory.create(product_range=product_range, barcode=barcode)
    product_range.complete_new_range(user)
    product.refresh_from_db()
    assert product.barcode == barcode


@pytest.mark.django_db
@pytest.mark.parametrize(
    "product_count,expected",
    ((0, False), (1, False), (2, True), (3, True)),
)
def test_has_variations_method(product_count, expected, product_factory, product_range):
    product_factory.create_batch(product_count, product_range=product_range)
    assert product_range.has_variations() is expected


@pytest.mark.django_db
def test_variation_options_method(variation_range):
    assert set(variation_range.variation_options()) == set(["Colour", "Size"])


@pytest.mark.django_db
def test_listing_attributes_method(variation_range):
    assert set(variation_range.listing_attributes()) == set(["Design", "Quantity"])


@pytest.mark.django_db
def test_variation_option_values_method(variation_range):
    assert variation_range.variation_option_values() == {
        "Colour": ["Blue", "Green", "Red"],
        "Size": ["Large", "Medium", "Small"],
    }


@pytest.mark.django_db
def test_variation_values_method(variation_range):
    assert set(variation_range.variation_values()) == {
        "Blue",
        "Green",
        "Red",
        "Large",
        "Medium",
        "Small",
    }


@pytest.mark.django_db
def test_listing_attribute_values_method(variation_range):
    assert set(variation_range.listing_attribute_values()) == {"Rectangular", "5"}


@pytest.mark.django_db
@pytest.mark.parametrize(
    "status,in_qs",
    (
        (models.ProductRange.COMPLETE, True),
        (models.ProductRange.CREATING, False),
        (models.ProductRange.ERROR, False),
    ),
)
def test_ranges_manager_queryset(status, in_qs, product_range_factory):
    product_range = product_range_factory.create(status=status)
    queryset = models.ProductRange.ranges.all()
    assert bool(product_range in queryset) is in_qs


@pytest.mark.django_db
@pytest.mark.parametrize(
    "status,in_qs",
    (
        (models.ProductRange.COMPLETE, False),
        (models.ProductRange.CREATING, True),
        (models.ProductRange.ERROR, False),
    ),
)
def test_creating_manager_queryset(status, in_qs, product_range_factory):
    product_range = product_range_factory.create(status=status)
    queryset = models.ProductRange.creating.all()
    assert bool(product_range in queryset) is in_qs
