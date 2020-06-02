import pytest

from price_calculator import models


@pytest.fixture
def name():
    return "Test Product Type"


@pytest.fixture
def new_package_type(name):
    package_type = models.ProductType(name=name)
    package_type.save()
    return package_type


@pytest.mark.django_db
def test_sets_name(new_package_type, name):
    assert new_package_type.name == name


@pytest.mark.django_db
def test__str__method(name, product_type_factory):
    package_type = product_type_factory.create(name=name)
    assert str(package_type) == name
