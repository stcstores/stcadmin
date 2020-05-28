import pytest

from price_calculator import models


@pytest.fixture
def name():
    return "Test VAT Rate"


@pytest.fixture
def cc_id():
    return 7


@pytest.fixture
def percentage():
    return 37


@pytest.fixture
def new_VAT_rate(name, cc_id, percentage):
    rate = models.VATRate(name=name, cc_id=cc_id, percentage=percentage)
    rate.save()
    return rate


@pytest.mark.django_db
def test_sets_name(new_VAT_rate, name):
    assert new_VAT_rate.name == name


@pytest.mark.django_db
def test_sets_cc_id(new_VAT_rate, cc_id):
    assert new_VAT_rate.cc_id == cc_id


@pytest.mark.django_db
def test_sets_percentage(new_VAT_rate, percentage):
    assert new_VAT_rate.percentage == percentage


@pytest.mark.django_db
def test__str__method(vat_rate_factory, name):
    assert str(vat_rate_factory.build(name=name)) == name
