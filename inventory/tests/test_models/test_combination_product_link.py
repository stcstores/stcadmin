import pytest
from django.db.utils import IntegrityError

from inventory import models


@pytest.fixture
def combination_product_link(combination_product_link_factory):
    return combination_product_link_factory.create()


@pytest.mark.django_db
def test_factory(combination_product_link):
    combination_product_link.full_clean()


@pytest.mark.django_db
def test_has_product_attribute(combination_product_link):
    assert isinstance(combination_product_link.product, models.Product)


@pytest.mark.django_db
def test_product_cannot_be_null(combination_product_link_factory):
    with pytest.raises(IntegrityError):
        combination_product_link_factory.create(product=None)


@pytest.mark.django_db
def test_has_combination_product_attribute(combination_product_link):
    assert isinstance(
        combination_product_link.combination_product, models.CombinationProduct
    )


@pytest.mark.django_db
def test_combination_product_cannot_be_null(combination_product_link_factory):
    with pytest.raises(IntegrityError):
        combination_product_link_factory.create(combination_product=None)


@pytest.mark.django_db
def test_has_quantity_attribute(combination_product_link):
    assert isinstance(combination_product_link.quantity, int)


@pytest.mark.django_db
def test_quantity_cannot_be_null(combination_product_link_factory):
    with pytest.raises(IntegrityError):
        combination_product_link_factory.create(quantity=None)


@pytest.mark.django_db
def test_str_method(combination_product_link_factory):
    combination_product_link = combination_product_link_factory.create(
        combination_product__sku="AAA-BBB-CCC", product__sku="AAA-BBB-111", quantity=5
    )
    assert str(combination_product_link) == "AAA-BBB-CCC contains 5 AAA-BBB-111"
