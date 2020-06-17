from unittest.mock import Mock, patch

import pytest
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
    def _mock_product(vat_rate_id, department_id, purchase_price):
        department = Mock(id=department_id)
        purchase_price = Mock(value=purchase_price)
        return Mock(
            vat_rate_id=vat_rate_id,
            options={"Department": department, "Purchase Price": purchase_price},
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
def test_sets_details_set(new_product_sale):
    assert new_product_sale.error is None


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
    vat_rate,
    purchase_price,
    vat_rate_factory,
    product_sale_factory,
):
    vat_rate_obj = vat_rate_factory.create(percentage=vat_rate)
    mock_CCAPI.get_product.return_value = mock_product(
        department_id=department.product_option_value_ID,
        vat_rate_id=vat_rate_obj.cc_id,
        purchase_price=float(purchase_price) / 100,
    )
    product_sale = product_sale_factory.create()
    product_sale.update_details()
    product_sale.refresh_from_db()
    return product_sale


@pytest.mark.django_db
def test_update_details_sets_error(updated_product):
    assert updated_product.error is False


@pytest.mark.django_db
def test_update_details_sets_department(updated_product, department):
    assert updated_product.department == department


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
    assert product_sale.error is True


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
    vat_rate,
    purchase_price,
    vat_rate_factory,
    product_sale_factory,
):
    vat_rate_obj = vat_rate_factory.create(percentage=vat_rate)
    mock_product = mock_product(
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
    assert product_sale.error is False


@pytest.mark.django_db
def test_update_product_details(
    mock_CCAPI,
    mock_product,
    department,
    vat_rate,
    purchase_price,
    vat_rate_factory,
    product_sale_factory,
):
    vat_rate_obj = vat_rate_factory.create(percentage=vat_rate)
    mock_CCAPI.get_product.return_value = mock_product(
        department_id=department.product_option_value_ID,
        vat_rate_id=vat_rate_obj.cc_id,
        purchase_price=float(purchase_price) / 100,
    )
    product_sale = product_sale_factory.create()
    models.ProductSale.objects.update_product_details()
    product_sale.refresh_from_db()
    assert product_sale.error is False


@pytest.mark.django_db
def test_update_product_details_does_not_stop_for_errors(
    mock_CCAPI, product_sale_factory,
):
    mock_CCAPI.get_product.side_effect = Exception
    product_sale_factory.create()
    models.ProductSale.objects.update_product_details()
