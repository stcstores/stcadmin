import pytest

from shipping import models


@pytest.fixture
def name():
    return "Test Provider"


@pytest.fixture
def new_provider(name):
    provider = models.Provider(name=name)
    provider.save()
    return provider


@pytest.mark.django_db
def test_name_is_set(name, new_provider):
    assert new_provider.name == name


@pytest.mark.django_db
def test_active_is_set(new_provider):
    assert new_provider.active is False


@pytest.mark.django_db
def test_str_method(provider_factory):
    provider = provider_factory.create()
    assert str(provider) == provider.name
