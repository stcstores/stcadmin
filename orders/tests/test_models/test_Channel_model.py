import pytest

from orders import models


@pytest.fixture
def name():
    return "Amazon UK"


@pytest.fixture
def new_channel(name):
    channel = models.Channel(name=name)
    channel.save()
    return channel


@pytest.mark.django_db
def test_sets_name(new_channel, name):
    assert new_channel.name == name


@pytest.mark.django_db
def test_defualt_channel_fee(new_channel):
    assert new_channel.channel_fee == 15.5


@pytest.mark.django_db
def test__str__method(channel_factory, name):
    assert str(channel_factory.create(name=name)) == name
