import pytest

from price_calculator import models


@pytest.fixture
def name():
    return "Test Channel Fee"


@pytest.fixture
def fee_percentage():
    return 9


@pytest.fixture
def country(country_factory):
    return country_factory.create()


@pytest.fixture
def new_channel_fee(name, country, fee_percentage):
    channel_fee = models.ChannelFee(
        name=name, country=country, fee_percentage=fee_percentage
    )
    channel_fee.save()
    return channel_fee


@pytest.mark.django_db
def test_sets_name(new_channel_fee, name):
    assert new_channel_fee.name == name


@pytest.mark.django_db
def test_sets_fee_percentage(new_channel_fee, fee_percentage):
    assert new_channel_fee.fee_percentage == fee_percentage


@pytest.mark.django_db
def test_sets_country(new_channel_fee, country):
    assert new_channel_fee.country == country


@pytest.mark.django_db
def test_sets_ordering(new_channel_fee):
    assert new_channel_fee.ordering == 100


@pytest.mark.django_db
def test__str__method(channel_fee_factory, name):
    assert str(channel_fee_factory.create(name=name)) == name


@pytest.mark.django_db
def test_is_ordered_by_ordering_field(channel_fee_factory):
    ordering_values = [500, 4, 256]
    for ordering in ordering_values:
        channel_fee_factory.create(ordering=ordering)
    assert [_.ordering for _ in models.ChannelFee.objects.all()] == sorted(
        ordering_values
    )
