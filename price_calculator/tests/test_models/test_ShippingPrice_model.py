import pytest

from price_calculator import models


@pytest.fixture
def name():
    return "Test Shipping Price"


@pytest.fixture
def country():
    return models.DestinationCountry.objects.create(name="Test Country")


@pytest.fixture
def package_type():
    return models.PackageType.objects.create()


@pytest.fixture
def min_weight():
    return 100


@pytest.fixture
def max_weight():
    return 1000


@pytest.fixture
def min_price():
    return 570


@pytest.fixture
def max_price():
    return 41000


@pytest.fixture
def item_price():
    return 550


@pytest.fixture
def kilo_price():
    return 252


@pytest.fixture
def vat_rate(vat_rate_factory):
    return vat_rate_factory.create()


@pytest.fixture
def new_shipping_price(name, country, item_price, kilo_price):
    shipping_price = models.ShippingPrice(
        name=name, country=country, item_price=item_price
    )
    shipping_price.save()
    return shipping_price


@pytest.mark.django_db
def test_sets_name(new_shipping_price, name):
    assert new_shipping_price.name == name


@pytest.mark.django_db
def test_sets_country(new_shipping_price, country):
    assert new_shipping_price.country == country


@pytest.mark.django_db
def test_sets_min_weight(new_shipping_price):
    assert new_shipping_price.min_weight is None


@pytest.mark.django_db
def test_sets_max_weight(new_shipping_price):
    assert new_shipping_price.max_weight is None


@pytest.mark.django_db
def test_sets_min_price(new_shipping_price):
    assert new_shipping_price.min_price is None


@pytest.mark.django_db
def test_sets_max_price(new_shipping_price):
    assert new_shipping_price.max_price is None


@pytest.mark.django_db
def test_sets_item_price(new_shipping_price, item_price):
    assert new_shipping_price.item_price == item_price


@pytest.mark.django_db
def test_sets_kilo_price(new_shipping_price):
    assert new_shipping_price.kilo_price is None


@pytest.mark.django_db
def test_sets_disabled(new_shipping_price):
    assert new_shipping_price.disabled is False


@pytest.mark.django_db
def can_set_package_type(new_shipping_price, package_type):
    new_shipping_price.package_type.set([package_type])
    assert list(new_shipping_price.package_type.all()) == [package_type]


@pytest.mark.django_db
def can_set_VAT_rate(new_shipping_price, vat_rate):
    new_shipping_price.vat_rate.set([vat_rate])
    assert list(new_shipping_price.vat_rate.all()) == [vat_rate]


@pytest.mark.django_db
def test__str__method(shipping_price_factory, name):
    assert str(shipping_price_factory.create(name=name)) == name


@pytest.mark.django_db
@pytest.mark.parametrize(
    "kilo_price,weight,expected",
    (
        (500, 2000, 1000),
        (500, 50, 25),
        (500, 10, 5),
        (140, 2000, 280),
        (140, 50, 7),
        (140, 10, 1),
        (None, 2000, 0),
        (None, 50, 0),
        (None, 10, 0),
    ),
)
def test_calculate_kilos_method(kilo_price, weight, expected, shipping_price_factory):
    shipping_price = shipping_price_factory.create(kilo_price=kilo_price)
    assert shipping_price.calculate_kilos(weight) == expected


@pytest.mark.django_db
@pytest.mark.parametrize(
    "kilo_price,weight,expected",
    (
        (500, 2000, 1025),
        (500, 50, 50),
        (500, 10, 30),
        (140, 2000, 305),
        (140, 50, 32),
        (140, 10, 26),
        (None, 2000, 25),
        (None, 50, 25),
        (None, 10, 25),
    ),
)
def test_calculate_method(kilo_price, weight, expected, shipping_price_factory):
    shipping_price = shipping_price_factory.create(item_price=25, kilo_price=kilo_price)
    assert shipping_price.calculate(weight) == expected


@pytest.mark.django_db
def test_package_type_string_method(package_type_factory, shipping_price_factory):
    package_types = [
        package_type_factory.create(name=name) for name in ("Foo", "Bar", "Baz")
    ]
    shipping_price = shipping_price_factory.create()
    shipping_price.package_type.set(package_types)
    assert shipping_price.package_type_string() == "Foo, Bar, Baz"


@pytest.mark.django_db
def test_get_price_method(country, package_type, shipping_price_factory):
    shipping_price = shipping_price_factory.create(
        country=country, min_weight=250, max_weight=500, min_price=1000, max_price=8000
    )
    shipping_price.package_type.set([package_type])
    assert (
        models.ShippingPrice.get_price(country.name, package_type.name, 300, 1500)
        == shipping_price
    )


@pytest.mark.django_db
def test_get_price_method_without_match(country, package_type, shipping_price_factory):
    shipping_price = shipping_price_factory.create(
        country=country, min_weight=250, max_weight=500, min_price=1000, max_price=8000
    )
    shipping_price.package_type.set([package_type])
    with pytest.raises(models.DestinationCountry.NoShippingService):
        models.ShippingPrice.get_price(country.name, package_type.name, 15000, 1500)
