import pytest

from price_calculator import models


@pytest.fixture
def name():
    return "Test Shipping Price"


@pytest.fixture
def country(country_factory):
    return country_factory.create()


@pytest.fixture
def shipping_service(shipping_service_factory):
    return shipping_service_factory.create()


@pytest.fixture
def product_type():
    return models.ProductType.objects.create()


@pytest.fixture
def channel(channel_factory):
    return channel_factory.create()


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
def vat_rate(vat_rate_factory):
    return vat_rate_factory.create()


@pytest.fixture
def new_shipping_method(name, country, shipping_service):
    shipping_method = models.ShippingMethod(
        name=name, country=country, shipping_service=shipping_service
    )
    shipping_method.save()
    return shipping_method


@pytest.mark.django_db
def test_sets_name(new_shipping_method, name):
    assert new_shipping_method.name == name


@pytest.mark.django_db
def test_sets_country(new_shipping_method, country):
    assert new_shipping_method.country == country


@pytest.mark.django_db
def test_sets_min_weight(new_shipping_method):
    assert new_shipping_method.min_weight == 0


@pytest.mark.django_db
def test_sets_max_weight(new_shipping_method):
    assert new_shipping_method.max_weight is None


@pytest.mark.django_db
def test_sets_min_price(new_shipping_method):
    assert new_shipping_method.min_price == 0


@pytest.mark.django_db
def test_sets_max_price(new_shipping_method):
    assert new_shipping_method.max_price is None


@pytest.mark.django_db
def test_sets_inactive(new_shipping_method):
    assert new_shipping_method.inactive is False


@pytest.mark.django_db
def can_set_product_type(new_shipping_method, product_type):
    new_shipping_method.product_type.set([product_type])
    assert list(new_shipping_method.product_type.all()) == [product_type]


@pytest.mark.django_db
def can_set_channel_type(new_shipping_method, channel):
    new_shipping_method.channel.set([channel])
    assert list(new_shipping_method.channel.all()) == [channel]


@pytest.mark.django_db
def can_set_VAT_rate(new_shipping_method, vat_rate):
    new_shipping_method.vat_rate.set([vat_rate])
    assert list(new_shipping_method.vat_rate.all()) == [vat_rate]


@pytest.mark.django_db
def test__str__method(shipping_method_factory, name):
    assert str(shipping_method_factory.create(name=name)) == name


@pytest.mark.django_db
def test_product_type_string_method(product_type_factory, shipping_method_factory):
    product_types = [
        product_type_factory.create(name=name) for name in ("Foo", "Bar", "Baz")
    ]
    shipping_method = shipping_method_factory.create()
    shipping_method.product_type.set(product_types)
    assert shipping_method.product_type_string() == "Foo, Bar, Baz"


@pytest.mark.django_db
def test__get_shipping_price_method(
    shipping_price_factory, shipping_method_factory, country, shipping_service
):
    shipping_price = shipping_price_factory.create(
        country=country, shipping_service=shipping_service
    )
    shipping_method = shipping_method_factory.create(
        country=country, shipping_service=shipping_service
    )
    assert shipping_method._get_shipping_price() == shipping_price


@pytest.mark.django_db
def test__get_shipping_price_raises(shipping_method_factory):
    shipping_method = shipping_method_factory.create()
    with pytest.raises(models.NoShippingService):
        shipping_method._get_shipping_price()


@pytest.mark.django_db
def test_shipping_price_method(
    shipping_price_factory, shipping_method_factory, country, shipping_service
):
    weight = 500
    shipping_price = shipping_price_factory.create(
        country=country, shipping_service=shipping_service
    )
    shipping_method = shipping_method_factory.create(
        country=country, shipping_service=shipping_service
    )
    assert shipping_method.shipping_price(weight) == shipping_price.price(weight)
