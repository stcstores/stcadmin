import pytest

from hardware import models


@pytest.fixture
def name(name_factory):
    return name_factory.create()


@pytest.fixture
def available_name(name_factory):
    return name_factory.create(is_available=True)


@pytest.fixture
def unavailable_name(name_factory):
    return name_factory.create(is_available=False)


@pytest.mark.django_db
def test_full_clean(name):
    assert name.full_clean() is None


# Test Attributes


@pytest.mark.django_db
def test_has_name_attribute(name):
    assert isinstance(name.name, str)


@pytest.mark.django_db
def test_has_is_available_attribute(name):
    assert isinstance(name.is_available, bool)


# Test Manager


@pytest.mark.django_db
def test_available_manager(available_name, unavailable_name):
    qs = models.Name.available.all()
    assert qs.contains(available_name)
    assert qs.contains(unavailable_name) is False


@pytest.mark.django_db
def test_available_manager_get_name_method(available_name, unavailable_name):
    assert models.Name.available.get_name() == available_name
    assert models.Name.available.get_name() == available_name
    assert models.Name.available.get_name() == available_name


# Test Methods


@pytest.mark.django_db
def test_str_method(name):
    assert str(name) == name.name


@pytest.mark.django_db
def test_network_safe_method(name_factory):
    name = name_factory.create(name="Joe Bloggs")
    assert name.network_safe() == "JOE_BLOGGS"


@pytest.mark.django_db
def test_use_method(available_name):
    available_name.use()
    available_name.refresh_from_db()
    assert available_name.is_available is False
