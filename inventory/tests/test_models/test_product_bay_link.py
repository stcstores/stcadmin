import datetime as dt

import pytest

from inventory import models


@pytest.fixture
def product_bay_link(product_bay_link_factory):
    product_bay_link = product_bay_link_factory.create()
    product_bay_link.full_clean()
    return product_bay_link


@pytest.mark.django_db
def test_product_bay_link_has_product_attribute(product_bay_link):
    assert isinstance(product_bay_link.product, models.Product)


@pytest.mark.django_db
def test_product_bay_link_has_bay_attribute(product_bay_link):
    assert isinstance(product_bay_link.bay, models.Bay)


@pytest.mark.django_db
def test_product_bay_link_has_create_at_attribute(product_bay_link):
    assert isinstance(product_bay_link.created_at, dt.datetime)


@pytest.mark.django_db
def test_product_bay_link_has_modified_at_attribute(product_bay_link):
    assert isinstance(product_bay_link.modified_at, dt.datetime)


@pytest.mark.django_db
def test_product_bay_link_str_method(product_bay_link_factory):
    link = product_bay_link_factory.create(
        product__sku="AAA-AAA-AAA",
        product__product_range__name="Product Name",
        bay__name="Bay Name",
    )
    assert str(link) == f"Bay Link: {link.product} - {link.bay}"
