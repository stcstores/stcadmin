from unittest.mock import Mock, patch

import pytest
from django.core.exceptions import ObjectDoesNotExist
from django.db import IntegrityError

from orders import models


@pytest.fixture
def order(order_factory):
    return order_factory.create()


@pytest.fixture
def product_ID():
    return "484894684"


@pytest.fixture
def sku():
    return '"ABC-213-JKE'


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
def department(department_factory):
    return department_factory.create()


@pytest.fixture
def supplier(supplier_factory):
    return supplier_factory.create()


@pytest.fixture
def vat_rate():
    return 20


@pytest.fixture
def purchase_price():
    return 680


@pytest.fixture
def mock_CCAPI():
    with patch("orders.models.product_sale.CCAPI") as mock_ccapi:
        yield mock_ccapi


@pytest.fixture
def mock_product():
    def _mock_product(vat_rate_id, department_id, supplier_id, purchase_price):
        department = Mock(value=Mock(id=int(department_id)))
        supplier = Mock(value=Mock(id=int(supplier_id)))
        purchase_price = Mock(value=Mock(value=float(purchase_price)))
        return Mock(
            vat_rate_id=vat_rate_id,
            options={
                "Department": department,
                "Purchase Price": purchase_price,
                "Supplier": supplier,
            },
        )

    return _mock_product


@pytest.fixture
def new_product_sale(
    order,
    product_ID,
    sku,
    name,
    weight,
    quantity,
    price,
    department,
    supplier,
    vat_rate,
    purchase_price,
):
    sale = models.ProductSale(
        order=order,
        product_ID=product_ID,
        sku=sku,
        name=name,
        weight=weight,
        quantity=quantity,
        price=price,
        department=department,
        supplier=supplier,
        vat_rate=vat_rate,
        purchase_price=purchase_price,
    )
    sale.save()
    return sale


@pytest.mark.django_db
def test_sets_order(new_product_sale, order):
    assert new_product_sale.order == order


@pytest.mark.django_db
def test_sets_product_ID(new_product_sale, product_ID):
    assert new_product_sale.product_ID == product_ID


@pytest.mark.django_db
def test_sets_sku(new_product_sale, sku):
    assert new_product_sale.sku == sku


@pytest.mark.django_db
def test_sku_defaults_null(
    order,
    product_ID,
    name,
    weight,
    quantity,
    price,
    department,
    vat_rate,
    purchase_price,
):
    sale = models.ProductSale(
        order=order,
        product_ID=product_ID,
        name=name,
        weight=weight,
        quantity=quantity,
        price=price,
        department=department,
        purchase_price=purchase_price,
        vat_rate=vat_rate,
    )
    sale.save()
    sale.refresh_from_db()
    assert sale.sku is None


@pytest.mark.django_db
def test_sets_name(new_product_sale, name):
    assert new_product_sale.name == name


@pytest.mark.django_db
def test_name_defaults_null(order, product_ID, sku, weight, quantity, price):
    sale = models.ProductSale(
        order=order,
        product_ID=product_ID,
        sku=sku,
        weight=weight,
        quantity=quantity,
        price=price,
    )
    sale.save()
    sale.refresh_from_db()
    assert sale.name is None


@pytest.mark.django_db
def test_weight_defaults_null(order, product_ID, sku, name, quantity, price):
    sale = models.ProductSale(
        order=order,
        product_ID=product_ID,
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
def test_sets_department(new_product_sale, department):
    assert new_product_sale.department == department


@pytest.mark.django_db
def test_department_defaults_to_null(order, product_ID, sku, name, quantity, price):
    sale = models.ProductSale(
        order=order, product_ID=product_ID, sku=sku, quantity=quantity, price=price,
    )
    sale.save()
    sale.refresh_from_db()
    assert sale.department is None


@pytest.mark.django_db
def test_sets_purchase_price(new_product_sale, purchase_price):
    assert new_product_sale.purchase_price == purchase_price


@pytest.mark.django_db
def test_purchase_price_defaults_to_null(order, product_ID, sku, name, quantity, price):
    sale = models.ProductSale(
        order=order, product_ID=product_ID, sku=sku, quantity=quantity, price=price,
    )
    sale.save()
    sale.refresh_from_db()
    assert sale.purchase_price is None


@pytest.mark.django_db
def test_sets_vat_rate(new_product_sale, vat_rate):
    assert new_product_sale.vat_rate == vat_rate


@pytest.mark.django_db
def test_vat_rate_defaults_to_null(order, product_ID, sku, name, quantity, price):
    sale = models.ProductSale(
        order=order, product_ID=product_ID, sku=sku, quantity=quantity, price=price,
    )
    sale.save()
    sale.refresh_from_db()
    assert sale.vat_rate is None


@pytest.mark.django_db
def test_sets_supplier(new_product_sale, supplier):
    assert new_product_sale.supplier == supplier


@pytest.mark.django_db
def test_supplier_defaults_null(
    order,
    product_ID,
    name,
    weight,
    quantity,
    price,
    department,
    vat_rate,
    purchase_price,
):
    sale = models.ProductSale(
        order=order,
        product_ID=product_ID,
        name=name,
        weight=weight,
        quantity=quantity,
        price=price,
        department=department,
        purchase_price=purchase_price,
        vat_rate=vat_rate,
    )
    sale.save()
    sale.refresh_from_db()
    assert sale.supplier is None


@pytest.mark.django_db
def test_sets_details_success(new_product_sale):
    assert new_product_sale.details_success is None


@pytest.mark.django_db
def test_order_and_product_ID_are_unique_together(
    order, product_ID, product_sale_factory
):
    product_sale_factory.create(order=order, product_ID=product_ID)
    with pytest.raises(IntegrityError):
        product_sale_factory.create(order=order, product_ID=product_ID)


@pytest.fixture
def updated_product(
    mock_CCAPI,
    mock_product,
    department,
    supplier,
    vat_rate,
    purchase_price,
    vat_rate_factory,
    product_sale_factory,
):
    vat_rate_obj = vat_rate_factory.create(percentage=vat_rate)
    mock_CCAPI.get_product.return_value = mock_product(
        supplier_id=supplier.product_option_value_ID,
        department_id=department.product_option_value_ID,
        vat_rate_id=vat_rate_obj.cc_id,
        purchase_price=float(purchase_price) / 100,
    )
    product_sale = product_sale_factory.create()
    product_sale.update_details()
    product_sale.refresh_from_db()
    return product_sale


@pytest.mark.django_db
def test_update_details_sets_details_success(updated_product):
    assert updated_product.details_success is True


@pytest.mark.django_db
def test_update_details_sets_department(updated_product, department):
    assert updated_product.department == department


@pytest.mark.django_db
def test_update_details_sets_supplier(updated_product, supplier):
    assert updated_product.supplier == supplier


@pytest.mark.django_db
def test_update_details_sets_purchase_price(updated_product, purchase_price):
    assert updated_product.purchase_price == purchase_price


@pytest.mark.django_db
def test_update_details_sets_vat_rate(updated_product, vat_rate):
    assert updated_product.vat_rate == vat_rate


@pytest.mark.django_db
def test_update_details_marks_updated_on_exception(mock_CCAPI, product_sale_factory):
    mock_CCAPI.get_product.side_effect = Exception
    product_sale = product_sale_factory.create()
    with pytest.raises(Exception):
        product_sale.update_details()
    product_sale.refresh_from_db()
    assert product_sale.details_success is False


@pytest.mark.django_db
def test_update_details_retry_count(mock_CCAPI, product_sale_factory):
    mock_CCAPI.get_product.side_effect = Exception
    product_sale = product_sale_factory.create()
    with pytest.raises(Exception):
        product_sale.update_details()
    assert len(mock_CCAPI.get_product.mock_calls) == 10


@pytest.mark.django_db
def test_update_details_retries(
    mock_CCAPI,
    mock_product,
    department,
    supplier,
    vat_rate,
    purchase_price,
    vat_rate_factory,
    product_sale_factory,
):
    vat_rate_obj = vat_rate_factory.create(percentage=vat_rate)
    mock_product = mock_product(
        supplier_id=supplier.product_option_value_ID,
        department_id=department.product_option_value_ID,
        vat_rate_id=vat_rate_obj.cc_id,
        purchase_price=float(purchase_price) / 100,
    )
    mock_CCAPI.get_product.side_effect = [
        Exception,
        Exception,
        Exception,
        mock_product,
    ]
    product_sale = product_sale_factory.create()
    product_sale.update_details()
    assert len(mock_CCAPI.get_product.mock_calls) == 4
    assert product_sale.details_success is True


@pytest.mark.django_db
def test_does_not_retry_for_does_not_exist_exceptions(
    mock_CCAPI,
    mock_product,
    department,
    supplier,
    purchase_price,
    vat_rate_factory,
    product_sale_factory,
):
    mock_product = mock_product(
        department_id=department.product_option_value_ID,
        supplier_id=supplier.product_option_value_ID,
        vat_rate_id="99999",
        purchase_price=float(purchase_price) / 100,
    )
    mock_CCAPI.get_product.return_value = mock_product
    product_sale = product_sale_factory.create()
    with pytest.raises(ObjectDoesNotExist):
        product_sale.update_details()
    mock_CCAPI.get_product.assert_called_once()


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
    "price,quantity,vat_rate,expected",
    [
        (550, 1, 0, 0),
        (550, 2, 0, 0),
        (720, 3, 0, 0),
        (550, 1, 20, 91),
        (550, 2, 20, 183),
        (720, 3, 20, 360),
    ],
)
def test__vat_paid(price, quantity, vat_rate, expected, product_sale_factory):
    sale = product_sale_factory.create(
        price=price, quantity=quantity, vat_rate=vat_rate
    )
    assert sale._vat_paid() == expected


@pytest.mark.django_db
@pytest.mark.parametrize(
    "price,quantity,expected", [(550, 1, 82), (550, 2, 165), (720, 3, 324)]
)
def test_channel_fee_paid(price, quantity, expected, product_sale_factory):
    sale = product_sale_factory.create(price=price, quantity=quantity)
    assert sale._channel_fee_paid() == expected


@pytest.mark.django_db
@pytest.mark.parametrize(
    "purchase_price,quantity,expected", [(550, 1, 550), (550, 2, 1100), (720, 3, 2160)]
)
def test_purchase_price_total(purchase_price, quantity, expected, product_sale_factory):
    sale = product_sale_factory.create(purchase_price=purchase_price, quantity=quantity)
    assert sale._purchase_price_total() == expected
