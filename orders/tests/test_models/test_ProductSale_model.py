import pytest
from django.db import IntegrityError

from orders import models


@pytest.fixture
def order(order_factory):
    return order_factory.create()


@pytest.fixture
def sku():
    return "ABC-213-JKE"


@pytest.fixture
def channel_sku():
    return "AMZ_0009562"


@pytest.fixture
def name():
    return "Test Product - Small - Red"


@pytest.fixture
def weight():
    return 235


@pytest.fixture
def quantity():
    return 3


@pytest.fixture
def price():
    return 550


@pytest.fixture
def supplier(supplier_factory):
    return supplier_factory.create()


@pytest.fixture
def vat():
    return 1250


@pytest.fixture
def purchase_price():
    return 680


@pytest.fixture
def new_product_sale(
    order,
    sku,
    name,
    channel_sku,
    weight,
    quantity,
    price,
    supplier,
    vat,
    purchase_price,
):
    sale = models.ProductSale(
        order=order,
        sku=sku,
        channel_sku=channel_sku,
        name=name,
        weight=weight,
        quantity=quantity,
        price=price,
        supplier=supplier,
        vat=vat,
        purchase_price=purchase_price,
    )
    sale.save()
    return sale


@pytest.mark.django_db
def test_sets_order(new_product_sale, order):
    assert new_product_sale.order == order


@pytest.mark.django_db
def test_sets_sku(new_product_sale, sku):
    assert new_product_sale.sku == sku


@pytest.mark.django_db
def test_sets_channel_sku(new_product_sale, channel_sku):
    assert new_product_sale.channel_sku == channel_sku


@pytest.mark.django_db
def test_sku_defaults_null(
    order,
    name,
    weight,
    quantity,
    price,
    vat,
    purchase_price,
):
    sale = models.ProductSale(
        order=order,
        name=name,
        weight=weight,
        quantity=quantity,
        price=price,
        purchase_price=purchase_price,
        vat=vat,
    )
    sale.save()
    sale.refresh_from_db()
    assert sale.sku is None


@pytest.mark.django_db
def test_sets_name(new_product_sale, name):
    assert new_product_sale.name == name


@pytest.mark.django_db
def test_name_defaults_null(order, sku, weight, quantity, price):
    sale = models.ProductSale(
        order=order,
        sku=sku,
        weight=weight,
        quantity=quantity,
        price=price,
    )
    sale.save()
    sale.refresh_from_db()
    assert sale.name is None


@pytest.mark.django_db
def test_weight_defaults_null(order, sku, name, quantity, price):
    sale = models.ProductSale(
        order=order,
        sku=sku,
        name=name,
        quantity=quantity,
        price=price,
    )
    sale.save()
    sale.refresh_from_db()
    assert sale.weight is None


@pytest.mark.django_db
def test_sets_weight(new_product_sale, weight):
    assert new_product_sale.weight == weight


@pytest.mark.django_db
def test_sets_quantity(new_product_sale, quantity):
    assert new_product_sale.quantity == quantity


@pytest.mark.django_db
def test_sets_price(new_product_sale, price):
    assert new_product_sale.price == price


@pytest.mark.django_db
def test_sets_purchase_price(new_product_sale, purchase_price):
    assert new_product_sale.purchase_price == purchase_price


@pytest.mark.django_db
def test_purchase_price_defaults_to_null(order, sku, name, quantity, price):
    sale = models.ProductSale(order=order, sku=sku, quantity=quantity, price=price)
    sale.save()
    sale.refresh_from_db()
    assert sale.purchase_price is None


@pytest.mark.django_db
def test_sets_vat(new_product_sale, vat):
    assert new_product_sale.vat == vat


@pytest.mark.django_db
def test_vat_defaults_to_null(order, sku, name, quantity, price):
    sale = models.ProductSale(order=order, sku=sku, quantity=quantity, price=price)
    sale.save()
    sale.refresh_from_db()
    assert sale.vat is None


@pytest.mark.django_db
def test_sets_supplier(new_product_sale, supplier):
    assert new_product_sale.supplier == supplier


@pytest.mark.django_db
def test_supplier_defaults_null(
    order,
    name,
    weight,
    quantity,
    price,
    vat,
    purchase_price,
):
    sale = models.ProductSale(
        order=order,
        name=name,
        weight=weight,
        quantity=quantity,
        price=price,
        purchase_price=purchase_price,
        vat=vat,
    )
    sale.save()
    sale.refresh_from_db()
    assert sale.supplier is None


@pytest.mark.django_db
def test_order_and_sku_are_unique_together(order, sku, product_sale_factory):
    product_sale_factory.create(order=order, sku=sku)
    with pytest.raises(IntegrityError):
        product_sale_factory.create(order=order, sku=sku)


@pytest.mark.django_db
@pytest.mark.parametrize(
    "weight,quantity,expected", [(500, 1, 500), (500, 2, 1000), (300, 3, 900)]
)
def test_total_weight(weight, quantity, expected, product_sale_factory):
    sale = product_sale_factory.create(weight=weight, quantity=quantity)
    assert sale.total_weight() == expected


@pytest.mark.django_db
@pytest.mark.parametrize(
    "price,quantity,expected", [(550, 1, 550), (550, 2, 1100), (720, 3, 2160)]
)
def test_price_paid(price, quantity, expected, product_sale_factory):
    sale = product_sale_factory.create(price=price, quantity=quantity)
    assert sale._price_paid() == expected


@pytest.mark.django_db
@pytest.mark.parametrize(
    "price,quantity,channel_fee, expected",
    [(550, 1, 15.5, 85), (550, 2, 15.5, 170), (720, 3, 15.5, 334), (720, 3, 0, 0)],
)
def test_channel_fee_paid(price, quantity, expected, channel_fee, product_sale_factory):
    sale = product_sale_factory.create(
        price=price, quantity=quantity, order__channel__channel_fee=channel_fee
    )
    assert sale._channel_fee_paid() == expected


@pytest.mark.django_db
@pytest.mark.parametrize(
    "purchase_price,quantity,expected", [(550, 1, 550), (550, 2, 1100), (720, 3, 2160)]
)
def test_purchase_price_total(purchase_price, quantity, expected, product_sale_factory):
    sale = product_sale_factory.create(purchase_price=purchase_price, quantity=quantity)
    assert sale._purchase_price_total() == expected
