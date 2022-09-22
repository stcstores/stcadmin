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
def tax():
    return 125


@pytest.fixture
def unit_price():
    return 550


@pytest.fixture
def item_price(quantity, unit_price):
    return unit_price * quantity


@pytest.fixture
def item_total_before_tax(tax, item_price):
    return item_price - tax


@pytest.fixture
def supplier(supplier_factory):
    return supplier_factory.create()


@pytest.fixture
def purchase_price():
    return 280


@pytest.fixture
def new_product_sale(
    order,
    sku,
    name,
    channel_sku,
    weight,
    quantity,
    supplier,
    purchase_price,
    tax,
    unit_price,
    item_price,
    item_total_before_tax,
):
    sale = models.ProductSale(
        order=order,
        sku=sku,
        channel_sku=channel_sku,
        name=name,
        weight=weight,
        quantity=quantity,
        supplier=supplier,
        tax=tax,
        purchase_price=purchase_price,
        unit_price=unit_price,
        item_price=item_price,
        item_total_before_tax=item_total_before_tax,
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
    weight,
    quantity,
):
    sale = models.ProductSale(
        order=order,
        weight=weight,
        quantity=quantity,
    )
    sale.save()
    sale.refresh_from_db()
    assert sale.sku is None


@pytest.mark.django_db
def test_sets_name(new_product_sale, name):
    assert new_product_sale.name == name


@pytest.mark.django_db
def test_name_defaults_null(order, sku, weight, quantity):
    sale = models.ProductSale(
        order=order,
        sku=sku,
        weight=weight,
        quantity=quantity,
    )
    sale.save()
    sale.refresh_from_db()
    assert sale.name is None


@pytest.mark.django_db
def test_weight_defaults_null(order, sku, name, quantity):
    sale = models.ProductSale(
        order=order,
        sku=sku,
        name=name,
        quantity=quantity,
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
def test_sets_unit_price(new_product_sale, unit_price):
    assert new_product_sale.unit_price == unit_price


@pytest.mark.django_db
def test_sets_item_price(new_product_sale, item_price):
    assert new_product_sale.item_price == item_price


@pytest.mark.django_db
def test_sets_item_total_before_tax(new_product_sale, item_total_before_tax):
    assert new_product_sale.item_total_before_tax == item_total_before_tax


@pytest.mark.django_db
def test_sets_purchase_price(new_product_sale, purchase_price):
    assert new_product_sale.purchase_price == purchase_price


@pytest.mark.django_db
def test_purchase_price_defaults_to_null(order, sku, quantity):
    sale = models.ProductSale(order=order, sku=sku, quantity=quantity)
    sale.save()
    sale.refresh_from_db()
    assert sale.purchase_price is None


@pytest.mark.django_db
def test_sets_tax(new_product_sale, tax):
    assert new_product_sale.tax == tax


@pytest.mark.django_db
def test_tax_defaults_to_null(order, sku, quantity):
    sale = models.ProductSale(order=order, sku=sku, quantity=quantity)
    sale.save()
    sale.refresh_from_db()
    assert sale.tax is None


@pytest.mark.django_db
def test_sets_supplier(new_product_sale, supplier):
    assert new_product_sale.supplier == supplier


@pytest.mark.django_db
def test_supplier_defaults_null(order, quantity):
    sale = models.ProductSale(order=order, quantity=quantity)
    sale.save()
    sale.refresh_from_db()
    assert sale.supplier is None


@pytest.mark.django_db
def test_order_and_sku_are_unique_together(order, sku, product_sale_factory):
    product_sale_factory.create(order=order, sku=sku)
    with pytest.raises(IntegrityError):
        product_sale_factory.create(order=order, sku=sku)


@pytest.mark.django_db
@pytest.mark.parametrize("weight,quantity", [(500, 1), (500, 2), (300, 3)])
def test_total_weight(weight, quantity, product_sale_factory):
    sale = product_sale_factory.create(weight=weight, quantity=quantity)
    assert sale.total_weight() == weight * quantity


@pytest.mark.django_db
@pytest.mark.parametrize(
    "purchase_price,quantity,expected", [(550, 1, 550), (550, 2, 1100), (720, 3, 2160)]
)
def test_purchase_price_total(purchase_price, quantity, expected, product_sale_factory):
    sale = product_sale_factory.create(purchase_price=purchase_price, quantity=quantity)
    assert sale._purchase_price_total() == expected
