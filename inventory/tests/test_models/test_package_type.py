import datetime as dt

import pytest

from inventory import models


@pytest.fixture
def package_type(package_type_factory):
    package_type = package_type_factory.create()
    package_type.full_clean
    return package_type


@pytest.fixture
def new_package_type():
    package_type = models.PackageType(name="New Package Type")
    package_type.save()
    return package_type


@pytest.mark.django_db
def test_package_type_has_name_attribute(package_type):
    assert isinstance(package_type.name, str)
    assert len(package_type.name) > 0


@pytest.mark.django_db
def test_package_type_as_large_letter_compatible_attribute(package_type):
    assert isinstance(package_type.large_letter_compatible, bool)


@pytest.mark.django_db
def test_package_type_large_letter_compatible_attribute_defaults_to_False(
    new_package_type,
):
    assert new_package_type.large_letter_compatible is False


@pytest.mark.django_db
def test_package_type_has_description_attribute(package_type):
    assert isinstance(package_type.description, str)


@pytest.mark.django_db
def test_package_type_description_attribute_can_be_empty(new_package_type):
    assert new_package_type.description == ""


@pytest.mark.django_db
def test_package_type_has_active_attribute(package_type):
    assert isinstance(package_type.active, bool)


@pytest.mark.django_db
def test_package_type_active_attribute_defaults_to_true(new_package_type):
    assert new_package_type.active is True


@pytest.mark.django_db
def test_package_type_has_created_at_attribute(package_type):
    assert isinstance(package_type.created_at, dt.datetime)


@pytest.mark.django_db
def test_package_type_has_modified_at_attribute(package_type):
    assert isinstance(package_type.modified_at, dt.datetime)


@pytest.mark.django_db
def test_package_type_str_method(package_type_factory):
    name = "New Package Type"
    package_type = package_type_factory.create(name=name)
    assert str(package_type) == name
