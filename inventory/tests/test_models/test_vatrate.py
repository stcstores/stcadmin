import datetime as dt

import pytest
from django.core.exceptions import ValidationError

from inventory import models


@pytest.fixture
def vat_rate(vat_rate_factory):
    vat_rate = vat_rate_factory.create()
    vat_rate.full_clean()
    return vat_rate


@pytest.fixture
def new_vat_rate():
    vat_rate = models.VATRate(name="New VAT Rate", percentage=0.25)
    vat_rate.save()
    return vat_rate


@pytest.mark.django_db
def test_vat_rate_has_name_attribute(vat_rate):
    assert isinstance(vat_rate.name, str)
    assert len(vat_rate.name) > 0


@pytest.mark.django_db
def test_vat_rate_has_percentage_attribute(vat_rate):
    assert isinstance(vat_rate.percentage, float)


@pytest.mark.django_db
def test_vat_rate_percentage_attribute_can_be_zero(vat_rate_factory):
    vat_rate_factory.create(percentage=0).full_clean()


@pytest.mark.django_db
def test_vat_rate_percentage_attribute_can_be_one(vat_rate_factory):
    vat_rate_factory.create(percentage=1).full_clean()


@pytest.mark.django_db
def test_vat_rate_percentage_attribute_can_be_between_zero_and_one(vat_rate_factory):
    vat_rate_factory.create(percentage=0.5).full_clean()


@pytest.mark.django_db
def test_vat_rate_percentage_attribute_cannot_be_less_than_zero(vat_rate_factory):
    with pytest.raises(ValidationError):
        vat_rate_factory.create(percentage=-0.9).full_clean()


@pytest.mark.django_db
def test_vat_rate_percentage_attribute_cannot_be_more_than_one(vat_rate_factory):
    with pytest.raises(ValidationError):
        vat_rate_factory.create(percentage=1.1).full_clean()


@pytest.mark.django_db
def test_vat_rate_has_ordering_attribute(vat_rate):
    assert isinstance(vat_rate.ordering, int)


@pytest.mark.django_db
def test_vat_rate_ordering_attribute_defaults_to_zero(new_vat_rate):
    assert new_vat_rate.ordering == 0


@pytest.mark.django_db
def test_vat_rate_has_created_at_attribute(vat_rate):
    assert isinstance(vat_rate.created_at, dt.datetime)


@pytest.mark.django_db
def test_vat_rate_has_modified_at_attribute(vat_rate):
    assert isinstance(vat_rate.modified_at, dt.datetime)


@pytest.mark.django_db
def test_vat_rate_str_method(vat_rate_factory):
    name = "New VAT Rate"
    vat_rate = vat_rate_factory.create(name=name)
    assert str(vat_rate) == name
