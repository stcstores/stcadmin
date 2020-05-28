import pytest

from price_calculator import models


@pytest.fixture
def name():
    return "Test Package Type"


@pytest.fixture
def new_package_type(name):
    package_type = models.PackageType(name=name)
    package_type.save()
    return package_type


@pytest.mark.django_db
def test_sets_name(new_package_type, name):
    assert new_package_type.name == name


@pytest.mark.django_db
def test__str__method(name, package_type_factory):
    package_type = package_type_factory.create(name=name)
    assert str(package_type) == name
