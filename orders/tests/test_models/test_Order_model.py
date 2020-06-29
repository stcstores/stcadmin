from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from django.utils import timezone

from orders import models


@pytest.fixture
def order_ID():
    return "38839822"


@pytest.fixture
def customer_ID():
    return "9938382"


@pytest.fixture
def recieved_at():
    return timezone.make_aware(datetime(2020, 2, 23, 13, 52, 12))


@pytest.fixture
def dispatched_at():
    return timezone.make_aware(datetime(2020, 2, 24, 11, 32, 6))


@pytest.fixture
def channel(channel_factory):
    return channel_factory.create()


@pytest.fixture
def channel_order_ID():
    return "384048338BK"


@pytest.fixture
def country(country_factory):
    return country_factory.create()


@pytest.fixture
def shipping_rule(shipping_rule_factory):
    return shipping_rule_factory.create()


@pytest.fixture
def courier_service(courier_service_factory):
    return courier_service_factory.create()


@pytest.fixture
def tracking_number():
    return "TK304930093421"


@pytest.fixture
def total_paid():
    return 550


@pytest.fixture
def total_paid_GBP():
    return 780


@pytest.fixture
def new_order(order_ID, recieved_at, channel, country, shipping_rule, courier_service):
    new_order = models.Order(
        order_ID=order_ID,
        recieved_at=recieved_at,
        country=country,
        shipping_rule=shipping_rule,
        courier_service=courier_service,
    )
    new_order.save()
    return new_order


@pytest.fixture
def mock_CCAPI():
    with patch("orders.models.order.CCAPI") as mock_CCAPI:
        mock_CCAPI.recent_orders_for_customer.return_value = {}
        yield mock_CCAPI


@pytest.fixture
def open_recent_order(mock_CCAPI, order_ID):
    mock_recent_order = Mock(order_id=order_ID, CANCELLED="Cancelled", status="open")
    mock_CCAPI.recent_orders_for_customer.return_value[order_ID] = mock_recent_order


@pytest.fixture
def cancelled_recent_order(mock_CCAPI, order_ID):
    mock_recent_order = Mock(
        order_id=order_ID, CANCELLED="Cancelled", status="Cancelled"
    )
    mock_CCAPI.recent_orders_for_customer.return_value[order_ID] = mock_recent_order


@pytest.fixture
def ignored_recent_order(mock_CCAPI, order_ID):
    mock_recent_order = Mock(order_id=order_ID, IGNORED="ignored", status="ignored")
    mock_CCAPI.recent_orders_for_customer.return_value[order_ID] = mock_recent_order


@pytest.fixture
def mock_product():
    def _mock_product(
        product_id="8384938",
        price=5.50,
        quantity=3,
        sku="SEV-DJ3-9DK",
        per_item_weight=256.35,
        product_full_name="Test Product - AB343",
    ):
        return Mock(
            product_id=product_id,
            price=price,
            quantity=quantity,
            sku=sku,
            per_item_weight=per_item_weight,
            product_full_name=product_full_name,
        )

    return _mock_product


@pytest.fixture
def mock_order(
    mock_product,
    order_ID,
    customer_ID,
    recieved_at,
    dispatched_at,
    channel,
    channel_order_ID,
    country,
    shipping_rule,
    tracking_number,
):
    def _mock_order(**kwargs):
        return Mock(
            order_id=kwargs.get("order_id") or order_ID,
            customer_id=kwargs.get("customer_id") or customer_ID,
            date_recieved=kwargs.get("date_recieved") or datetime(2020, 2, 15, 12, 35),
            dispatch_date=kwargs.get("dispatch_date") or datetime(2020, 2, 16, 10, 18),
            cancelled=kwargs.get("cancelled") or False,
            channel_name=kwargs.get("channel_name") or channel.name,
            external_transaction_id=kwargs.get("external_transaction_id")
            or channel_order_ID,
            delivery_country_code=kwargs.get("delivery_country_code")
            or country.country_ID,
            default_cs_rule_name=kwargs.get("default_cs_rule_name")
            or f"{shipping_rule.name} - {shipping_rule.courier_service.name}",
            tracking_code=kwargs.get("tracking_code") or tracking_number,
            products=kwargs.get("products") or [mock_product()],
            can_process_order=kwargs.get("can_process_order") or True,
            priority=kwargs.get("priority") or False,
            total_gross=kwargs.get("total_gross") or "5.69",
            total_gross_gbp=kwargs.get("total_gross_gbp") or "8.96",
        )

    return _mock_order


@pytest.mark.django_db
def test_sets_order_ID(new_order, order_ID):
    assert new_order.order_ID == order_ID


@pytest.mark.django_db
def test_customer_ID_defaults_to_None(new_order):
    assert new_order.customer_ID is None


@pytest.mark.django_db
def test_can_set_customer_ID(
    order_ID, recieved_at, country, shipping_rule, courier_service, customer_ID
):
    order = models.Order(
        order_ID=order_ID,
        recieved_at=recieved_at,
        country=country,
        shipping_rule=shipping_rule,
        courier_service=courier_service,
        customer_ID=customer_ID,
    )
    order.save()
    order.refresh_from_db()
    assert order.customer_ID == customer_ID


@pytest.mark.django_db
def test_sets_recieved_at(new_order, recieved_at):
    assert new_order.recieved_at == recieved_at


@pytest.mark.django_db
def test_dispatched_at_defaults_to_None(new_order):
    assert new_order.dispatched_at is None


@pytest.mark.django_db
def test_can_set_dispatched_at(
    order_ID, recieved_at, country, shipping_rule, courier_service, dispatched_at
):
    order = models.Order(
        order_ID=order_ID,
        recieved_at=recieved_at,
        country=country,
        shipping_rule=shipping_rule,
        courier_service=courier_service,
        dispatched_at=dispatched_at,
    )
    order.save()
    order.refresh_from_db()
    assert order.dispatched_at == dispatched_at


@pytest.mark.django_db
def test_cancelled_defaults_to_False(new_order):
    assert new_order.cancelled is False


@pytest.mark.django_db
def test_ignored_defautls_to_False(new_order):
    assert new_order.ignored is False


@pytest.mark.django_db
def test_channel_defaults_to_None(new_order):
    assert new_order.channel is None


@pytest.mark.django_db
def test_can_set_channel(
    order_ID, recieved_at, country, shipping_rule, courier_service, channel
):
    order = models.Order(
        order_ID=order_ID,
        recieved_at=recieved_at,
        country=country,
        shipping_rule=shipping_rule,
        courier_service=courier_service,
        channel=channel,
    )
    order.save()
    order.refresh_from_db()
    assert order.channel == channel


@pytest.mark.django_db
def test_channel_order_id_defaults_to_None(new_order):
    assert new_order.channel_order_ID is None


@pytest.mark.django_db
def test_can_set_channel_order_ID(
    order_ID, recieved_at, country, shipping_rule, courier_service, channel_order_ID
):
    order = models.Order(
        order_ID=order_ID,
        recieved_at=recieved_at,
        country=country,
        shipping_rule=shipping_rule,
        courier_service=courier_service,
        channel_order_ID=channel_order_ID,
    )
    order.save()
    order.refresh_from_db()
    assert order.channel_order_ID == channel_order_ID


@pytest.mark.django_db
def test_sets_country(new_order, country):
    assert new_order.country == country


@pytest.mark.django_db
def test_sets_shipping_rule(new_order, shipping_rule):
    assert new_order.shipping_rule == shipping_rule


@pytest.mark.django_db
def test_sets_courier_service(new_order, courier_service):
    assert new_order.courier_service == courier_service


@pytest.mark.django_db
def test_tracking_number_defaults_to_None(new_order):
    assert new_order.tracking_number is None


@pytest.mark.django_db
def test_can_set_tracking_number(
    order_ID, recieved_at, country, shipping_rule, courier_service, tracking_number
):
    order = models.Order(
        order_ID=order_ID,
        recieved_at=recieved_at,
        country=country,
        shipping_rule=shipping_rule,
        courier_service=courier_service,
        tracking_number=tracking_number,
    )
    order.save()
    order.refresh_from_db()
    assert order.tracking_number == tracking_number


@pytest.mark.django_db
def test_sets_total_paid(new_order):
    assert new_order.total_paid is None


@pytest.mark.django_db
def test_can_set_total_paid(
    order_ID, recieved_at, country, shipping_rule, courier_service, total_paid
):
    order = models.Order(
        order_ID=order_ID,
        recieved_at=recieved_at,
        country=country,
        shipping_rule=shipping_rule,
        courier_service=courier_service,
        total_paid=total_paid,
    )
    order.save()
    order.refresh_from_db()
    assert order.total_paid == total_paid


@pytest.mark.django_db
def test_sets_total_GBP(new_order):
    assert new_order.total_paid_GBP is None


@pytest.mark.django_db
def test_can_set_total_paid_GBP(
    order_ID, recieved_at, country, shipping_rule, courier_service, total_paid_GBP
):
    order = models.Order(
        order_ID=order_ID,
        recieved_at=recieved_at,
        country=country,
        shipping_rule=shipping_rule,
        courier_service=courier_service,
        total_paid_GBP=total_paid_GBP,
    )
    order.save()
    order.refresh_from_db()
    assert order.total_paid_GBP == total_paid_GBP


@pytest.mark.django_db
def test__str__method(order_factory):
    order = order_factory.create(order_ID="3849383")
    assert str(order) == "Order: 3849383"


def test_is_dispatched_returns_true_if_order_is_dispatched(
    order_factory, dispatched_at
):
    order = order_factory.build(dispatched_at=dispatched_at)
    assert order.is_dispatched() is True


def test_is_dispatched_returns_false_if_order_is_not_dispatched(order_factory):
    order = order_factory.build(dispatched_at=None)
    assert order.is_dispatched() is False


@pytest.mark.django_db
def test_check_cancelled_does_nothing_for_cancelled_orders(mock_CCAPI, order_factory):
    order = order_factory.create(cancelled=True)
    order.check_cancelled()
    mock_CCAPI.recent_orders_for_customer.assert_not_called()


@pytest.mark.django_db
def test_check_cancelled_does_nothing_if_customer_ID_is_none(mock_CCAPI, order_factory):
    order = order_factory.create(customer_ID=None)
    order.check_cancelled()
    mock_CCAPI.recent_orders_for_customer.assert_not_called()


@pytest.mark.django_db
def test_check_cancelled_requests_recent_orders(
    mock_CCAPI, order_factory, order_ID, customer_ID
):
    order = order_factory.create(
        order_ID=order_ID, customer_ID=customer_ID, cancelled=False
    )
    order.check_cancelled()
    mock_CCAPI.recent_orders_for_customer.assert_called_once_with(
        customer_ID=customer_ID
    )


@pytest.mark.django_db
def test_check_cancelled_marks_cancelled_orders(
    order_factory, order_ID, customer_ID, cancelled_recent_order
):
    order = order_factory.create(
        order_ID=order_ID, customer_ID=customer_ID, cancelled=False
    )
    order.check_cancelled()
    order.refresh_from_db()
    assert order.cancelled is True


@pytest.mark.django_db
def test_check_cancelled_marks_ignored_orders(
    order_factory, order_ID, customer_ID, ignored_recent_order
):
    order = order_factory.create(
        order_ID=order_ID, customer_ID=customer_ID, cancelled=False
    )
    order.check_cancelled()
    order.refresh_from_db()
    assert order.ignored is True


@pytest.mark.django_db
def test_check_cancelled_does_nothing_for_open_orders(
    order_factory, order_ID, customer_ID, open_recent_order
):
    order = order_factory.create(
        order_ID=order_ID, customer_ID=customer_ID, cancelled=False
    )
    order.check_cancelled()
    order.refresh_from_db()
    assert order.cancelled is False
    assert order.ignored is False


@pytest.mark.parametrize(
    "now,expected",
    [
        (datetime(2019, 12, 23), datetime(2019, 12, 20)),  # Monday
        (datetime(2019, 12, 24), datetime(2019, 12, 23)),  # Tuesday
        (datetime(2019, 12, 25), datetime(2019, 12, 24)),  # Wednesday
        (datetime(2019, 12, 26), datetime(2019, 12, 25)),  # Thursday
        (datetime(2019, 12, 27), datetime(2019, 12, 26)),  # Friday
        (datetime(2019, 12, 28), datetime(2019, 12, 27)),  # Saturday
        (datetime(2019, 12, 29), datetime(2019, 12, 27)),  # Sunday
    ],
)
@patch("orders.models.order.timezone.now")
def test_urgent_since(mock_now, now, expected):
    mock_now.return_value = timezone.make_aware(now)
    assert models.order.urgent_since() == timezone.make_aware(expected)


@pytest.mark.django_db
def test_order_details(
    mock_order,
    mock_product,
    order_ID,
    customer_ID,
    recieved_at,
    dispatched_at,
    channel,
    channel_order_ID,
    country,
    shipping_rule,
    tracking_number,
):
    mock_order = mock_order(total_gross="8.69", total_gross_gbp="12.56")
    order_details = models.Order.objects._cc_order_details(mock_order)
    assert order_details == {
        "order_ID": order_ID,
        "customer_ID": customer_ID,
        "recieved_at": timezone.make_aware(mock_order.date_recieved),
        "dispatched_at": timezone.make_aware(mock_order.dispatch_date),
        "cancelled": mock_order.cancelled,
        "channel": channel,
        "channel_order_ID": channel_order_ID,
        "country": country,
        "shipping_rule": shipping_rule,
        "courier_service": shipping_rule.courier_service,
        "tracking_number": tracking_number,
        "ignored": not mock_order.can_process_order,
        "total_paid": 869,
        "total_paid_GBP": 1256,
        "priority": mock_order.priority,
    }


def test_parse_dispatch_date():
    date_time = datetime(2020, 1, 26, 11, 55, 36)
    returned_value = models.Order.objects._parse_dispatch_date(date_time)
    assert returned_value == timezone.make_aware(date_time)


def test_parse_dispatch_date_for_undispatched_orders():
    returned_value = models.Order.objects._parse_dispatch_date(
        models.Order.DISPATCH_EPOCH
    )
    assert returned_value is None


@pytest.mark.django_db
def test_create_or_update_from_cc_order_creates_an_order(mock_order, order_ID):
    models.Order.objects._create_or_update_from_cc_order(mock_order())
    assert models.Order.objects.filter(order_ID=order_ID).exists()


@pytest.mark.django_db
def test_create_or_update_from_cc_order_sets_customer_ID(
    mock_order, order_ID, customer_ID
):
    models.Order.objects._create_or_update_from_cc_order(mock_order())
    assert models.Order.objects.get(order_ID=order_ID).customer_ID == customer_ID


@pytest.mark.django_db
def test_create_or_update_from_cc_order_sets_recieved_at(mock_order, order_ID):
    mock_order = mock_order()
    models.Order.objects._create_or_update_from_cc_order(mock_order)
    expected = timezone.make_aware(mock_order.date_recieved)
    assert models.Order.objects.get(order_ID=order_ID).recieved_at == expected


@pytest.mark.django_db
def test_create_or_update_from_cc_order_sets_dispatched_at(mock_order, order_ID):
    mock_order = mock_order()
    models.Order.objects._create_or_update_from_cc_order(mock_order)
    expected = timezone.make_aware(mock_order.dispatch_date)
    assert models.Order.objects.get(order_ID=order_ID).dispatched_at == expected


@pytest.mark.django_db
def test_create_or_update_from_cc_order_sets_cancelled(mock_order, order_ID):
    models.Order.objects._create_or_update_from_cc_order(mock_order())
    assert models.Order.objects.get(order_ID=order_ID).cancelled is False


@pytest.mark.django_db
def test_create_or_update_from_cc_order_sets_channel(mock_order, order_ID, channel):
    models.Order.objects._create_or_update_from_cc_order(mock_order())
    assert models.Order.objects.get(order_ID=order_ID).channel == channel


@pytest.mark.django_db
def test_create_or_update_from_cc_order_sets_shipping_rule(
    mock_order, order_ID, shipping_rule
):
    models.Order.objects._create_or_update_from_cc_order(mock_order())
    assert models.Order.objects.get(order_ID=order_ID).shipping_rule == shipping_rule


@pytest.mark.django_db
def test_create_or_update_from_cc_order_sets_courier_service(
    mock_order, order_ID, shipping_rule
):
    models.Order.objects._create_or_update_from_cc_order(mock_order())
    assert (
        models.Order.objects.get(order_ID=order_ID).courier_service
        == shipping_rule.courier_service
    )


@pytest.mark.django_db
def test_create_or_update_from_cc_order_sets_tracking_number(
    mock_order, order_ID, tracking_number
):
    models.Order.objects._create_or_update_from_cc_order(mock_order())
    assert (
        models.Order.objects.get(order_ID=order_ID).tracking_number == tracking_number
    )


@pytest.mark.django_db
def test_create_or_update_from_cc_order_sets_ignored(mock_order, order_ID):
    mock_order = mock_order()
    models.Order.objects._create_or_update_from_cc_order(mock_order)
    assert models.Order.objects.get(order_ID=order_ID).ignored is False


@pytest.mark.django_db
def test_create_or_update_from_cc_order_updates_order(
    mock_order, order_ID, order_factory
):
    mock_order = mock_order()
    order = order_factory.create(order_ID=order_ID, dispatched_at=None)
    models.Order.objects._create_or_update_from_cc_order(mock_order)
    order.refresh_from_db()
    assert order.dispatched_at == timezone.make_aware(mock_order.dispatch_date)


@pytest.mark.django_db
def test_dispatched_order_does_not_update(
    mock_order, order_ID, customer_ID, dispatched_at, order_factory
):
    order = order_factory.create(
        order_ID=order_ID, customer_ID=customer_ID, dispatched_at=dispatched_at
    )
    models.Order.objects._create_or_update_from_cc_order(
        mock_order(customer_id="376327")
    )
    order.refresh_from_db()
    assert order.customer_ID == customer_ID


@pytest.mark.django_db
def test_invalid_country_code(mock_order):
    mock_order = mock_order(delivery_country_code=9999)
    with pytest.raises(models.Order.CountryNotRecognisedError):
        models.Order.objects._create_or_update_from_cc_order(mock_order)


@pytest.mark.django_db
def test_invalid_shipping_rule(mock_order):
    mock_order = mock_order(default_cs_rule_name="Invalid Rule Name")
    order = models.Order.objects._create_or_update_from_cc_order(mock_order)
    assert order.shipping_rule is None
    assert order.courier_service is None


@pytest.mark.django_db
def test_get_orders_for_dispatch(mock_CCAPI, mock_order):
    mock_orders = [mock_order(order_id="294039830"), mock_order(order_id="856939380")]
    mock_CCAPI.get_orders_for_dispatch.return_value = mock_orders
    returned_value = models.Order.objects._get_orders_for_dispatch()
    assert returned_value == mock_orders
    mock_CCAPI.get_orders_for_dispatch.assert_called_once_with(
        order_type=0, number_of_days=0
    )


@pytest.mark.django_db
def test_get_dispatched_orders(mock_CCAPI, mock_order):
    mock_orders = [mock_order(order_id="294039830"), mock_order(order_id="856939380")]
    mock_CCAPI.get_orders_for_dispatch.return_value = mock_orders
    returned_value = models.Order.objects._get_dispatched_orders()
    assert returned_value == mock_orders
    mock_CCAPI.get_orders_for_dispatch.assert_called_once_with(
        order_type=1, number_of_days=1
    )


@pytest.mark.django_db
def test_get_dispatched_orders_takes_number_of_days(mock_CCAPI, mock_order):
    mock_orders = [mock_order(order_id="294039830"), mock_order(order_id="856939380")]
    mock_CCAPI.get_orders_for_dispatch.return_value = mock_orders
    returned_value = models.Order.objects._get_dispatched_orders(number_of_days=5)
    assert returned_value == mock_orders
    mock_CCAPI.get_orders_for_dispatch.assert_called_once_with(
        order_type=1, number_of_days=5
    )


@pytest.mark.django_db
def test_create_or_update_creates_order(country, channel, shipping_rule, mock_order):
    mock_order = mock_order(priority=True, total_gross="15.69", total_gross_gbp="12.78")
    models.Order.objects._create_or_update_from_cc_order(mock_order)
    assert models.Order.objects.filter(
        order_ID=str(mock_order.order_id),
        customer_ID=str(mock_order.customer_id),
        recieved_at=timezone.make_aware(mock_order.date_recieved),
        dispatched_at=timezone.make_aware(mock_order.dispatch_date),
        cancelled=False,
        ignored=False,
        channel=channel,
        channel_order_ID=mock_order.external_transaction_id,
        country=country,
        shipping_rule=shipping_rule,
        courier_service=shipping_rule.courier_service,
        tracking_number=mock_order.tracking_code,
        total_paid=1569,
        total_paid_GBP=1278,
        priority=True,
    ).exists()


@pytest.mark.django_db
def test_update_sales(order_factory, mock_CCAPI, mock_order, mock_product):
    order = order_factory.create()
    products = [
        mock_product(
            product_id="3849390",
            quantity=1,
            price=6.50,
            sku="ABC-456-342",
            product_full_name="Test Product 0",
            per_item_weight=256.35,
        ),
        mock_product(
            product_id="5461616",
            quantity=5,
            price=12.80,
            sku="SGE-F3D-5DJ",
            product_full_name="Test Product 1",
            per_item_weight=12.63,
        ),
        mock_product(
            product_id="9651664",
            quantity=3,
            price=0.99,
            sku="SD5-S85-6F6",
            product_full_name="Test Product 2",
            per_item_weight=1156.356,
        ),
    ]
    mock_order = mock_order(products=products)
    mock_CCAPI.get_orders_for_dispatch.return_value = mock_order
    models.Order.objects._update_sales(order, mock_order)
    for product in products:
        assert models.ProductSale.objects.filter(
            order=order,
            product_ID=product.product_id,
            quantity=product.quantity,
            price=int(product.price * 100),
            sku=product.sku,
            name=product.product_full_name,
            weight=int(product.per_item_weight),
        ).exists()


@pytest.mark.django_db
def test_update_sales_updates_existing_sales(
    order_factory, product_sale_factory, mock_CCAPI, mock_order, mock_product
):
    order = order_factory.create()
    product_id = "3849390"
    product_sale = product_sale_factory.create(
        order=order,
        product_ID=product_id,
        quantity=5,
        price=920,
        sku="ABE-1E3-3DE",
        name="Test Product 1",
        weight=256,
    )
    product = mock_product(
        product_id=product_id,
        quantity=3,
        price=0.99,
        sku="SD5-S85-6F6",
        product_full_name="Test Product 2",
        per_item_weight=1156.356,
    )
    products = [product]
    mock_order = mock_order(products=products)
    mock_CCAPI.get_orders_for_dispatch.return_value = mock_order
    models.Order.objects._update_sales(order, mock_order)
    assert models.ProductSale.objects.filter(
        id=product_sale.id,
        order=order,
        product_ID=product.product_id,
        sku=product.sku,
        weight=product.per_item_weight,
        name=product.product_full_name,
        quantity=product.quantity,
    ).exists()


@pytest.mark.django_db
def test_update_creates_undispatched_orders(mock_CCAPI, mock_order):
    mock_order = mock_order()
    mock_CCAPI.get_orders_for_dispatch.side_effect = [[mock_order], []]
    models.Order.objects.update_orders()
    assert models.Order.objects.filter(order_ID=mock_order.order_id).exists()


@pytest.mark.django_db
def test_update_creates_dispatched_orders(mock_CCAPI, mock_order):
    mock_order = mock_order()
    mock_CCAPI.get_orders_for_dispatch.side_effect = [[], [mock_order]]
    models.Order.objects.update_orders()
    assert models.Order.objects.filter(order_ID=mock_order.order_id).exists()


@pytest.mark.django_db
def test_update_cancels_orders(
    mock_CCAPI, cancelled_recent_order, mock_order, order_ID
):
    mock_order = mock_order(dispatch_date=models.Order.DISPATCH_EPOCH)
    mock_CCAPI.get_orders_for_dispatch.side_effect = [[], [mock_order]]
    models.Order.objects.update_orders()
    assert models.Order.objects.filter(
        order_ID=order_ID, dispatched_at=None, cancelled=True
    )


@pytest.mark.django_db
def test_product_sales_are_not_created_for_a_dispatched_order(
    order_factory, mock_CCAPI, mock_order
):
    order = order_factory.create()
    mock_order = mock_order(order_id=order.order_ID)
    mock_CCAPI.get_orders_for_dispatch.side_effect = [[mock_order], []]
    models.Order.objects.update_orders()
    assert (
        models.ProductSale.objects.filter(
            order__order_ID=order.order_ID,
            product_ID=mock_order.products[0].product_id,
        ).exists()
        is False
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    "kwargs,returned",
    [
        ({"dispatched_at": None}, False),
        ({"dispatched_at": timezone.make_aware(datetime(2020, 5, 1))}, True),
    ],
)
def test_dispatched(kwargs, returned, order_factory):
    order = order_factory.create(**kwargs)
    queryset = models.Order.objects.dispatched()
    assert (order in queryset) == returned


@pytest.mark.django_db
@pytest.mark.parametrize(
    "kwargs,returned",
    [
        ({"dispatched_at": None}, True),
        ({"dispatched_at": timezone.make_aware(datetime(2020, 5, 1))}, False),
    ],
)
def test_undispatched(kwargs, returned, order_factory):
    order = order_factory.create(**kwargs)
    queryset = models.Order.objects.undispatched()
    assert (order in queryset) == returned


@pytest.mark.django_db
@pytest.mark.parametrize(
    "kwargs,returned",
    [
        ({"shipping_rule__priority": True, "cancelled": False}, True),
        ({"shipping_rule__priority": True, "cancelled": True}, False),
        ({"shipping_rule__priority": False, "cancelled": True}, False),
        ({"shipping_rule__priority": False, "cancelled": False}, False),
    ],
)
def test_priority(kwargs, returned, order_factory):
    order = order_factory.create(**kwargs)
    queryset = models.Order.objects.priority()
    assert (order in queryset) == returned


@pytest.mark.django_db
@pytest.mark.parametrize(
    "kwargs,returned",
    [
        ({"shipping_rule__priority": True, "cancelled": False}, False),
        ({"shipping_rule__priority": True, "cancelled": True}, False),
        ({"shipping_rule__priority": False, "cancelled": True}, False),
        ({"shipping_rule__priority": False, "cancelled": False}, True),
    ],
)
def test_non_priority(kwargs, returned, order_factory):
    order = order_factory.create(**kwargs)
    queryset = models.Order.objects.non_priority()
    assert (order in queryset) == returned


@pytest.mark.django_db
@pytest.mark.parametrize(
    "kwargs,returned",
    [
        (
            {
                "recieved_at": timezone.make_aware(datetime(2020, 2, 21, 21, 0, 0)),
                "dispatched_at": None,
            },
            False,
        ),
        (
            {
                "recieved_at": timezone.make_aware(datetime(2020, 2, 19, 23, 59, 59)),
                "dispatched_at": None,
            },
            True,
        ),
        (
            {
                "recieved_at": timezone.make_aware(datetime(2020, 2, 21, 21, 0, 0)),
                "dispatched_at": timezone.make_aware(datetime(2020, 5, 1)),
            },
            False,
        ),
        (
            {
                "recieved_at": timezone.make_aware(datetime(2020, 2, 19, 23, 59, 59)),
                "dispatched_at": timezone.make_aware(datetime(2020, 5, 1)),
            },
            False,
        ),
    ],
)
@patch("orders.models.order.urgent_since")
def test_urgent(mock_urgent_since, kwargs, returned, order_factory):
    mock_urgent_since.return_value = timezone.make_aware(datetime(2020, 2, 20, 0, 0, 0))
    order = order_factory.create(**kwargs)
    queryset = models.Order.objects.urgent()
    assert (order in queryset) == returned


@pytest.mark.django_db
def test_profit_calculable(order_factory, product_sale_factory):
    order = order_factory.create(postage_price_success=True)
    product_sale_factory.create(order=order, details_success=True)
    assert list(models.Order.objects.profit_calculable()) == [order]


@pytest.mark.django_db
def test_profit_calculable_excludes_details_not_retrieved(
    order_factory, product_sale_factory
):
    order = order_factory.create(postage_price_success=True)
    product_sale_factory.create(order=order, details_success=None)
    assert order not in models.Order.objects.profit_calculable()


@pytest.mark.django_db
def test_profit_calculable_excludes_details_failures(
    order_factory, product_sale_factory
):
    order = order_factory.create(postage_price_success=True)
    product_sale_factory.create(order=order, details_success=False)
    assert order not in models.Order.objects.profit_calculable()


@pytest.mark.django_db
def test_profit_calculable_excludes_postage_price_failrues(
    order_factory, product_sale_factory
):
    order = order_factory.create(postage_price_success=False)
    product_sale_factory.create(order=order, details_success=True)
    assert order not in models.Order.objects.profit_calculable()


@pytest.mark.django_db
def test_profit_calculable_excludes_postage_price_not_retrieved(
    order_factory, product_sale_factory
):
    order = order_factory.create(postage_price_success=None)
    product_sale_factory.create(order=order, details_success=True)
    assert order not in models.Order.objects.profit_calculable()


@pytest.fixture
def shipping_price(country, shipping_rule, shipping_price_factory):
    return shipping_price_factory.create(
        country=country, shipping_service=shipping_rule.shipping_service
    )


@pytest.fixture
def order_without_shipping_price(country, shipping_rule, order_factory):
    return order_factory.create(
        country=country,
        shipping_rule=shipping_rule,
        postage_price=None,
        postage_price_success=None,
    )


@pytest.mark.django_db
def test_get_postage_price(country, shipping_rule, shipping_price, order_factory):
    order = order_factory.create(country=country, shipping_rule=shipping_rule)
    assert order._get_postage_price() == shipping_price.price(order.total_weight())


@pytest.mark.django_db
def test_set_postage_price_sets_postage_price(
    country, shipping_rule, shipping_price, order_factory
):
    order = order_factory.create(
        country=country,
        shipping_rule=shipping_rule,
        postage_price=None,
        postage_price_success=None,
    )
    order._set_postage_price()
    order.refresh_from_db()
    assert order.postage_price == shipping_price.price(order.total_weight())


@pytest.mark.django_db
def test_set_postage_price_sets_postage_price_success(
    country, shipping_rule, shipping_price, order_without_shipping_price
):
    order_without_shipping_price._set_postage_price()
    order_without_shipping_price.refresh_from_db()
    assert order_without_shipping_price.postage_price_success is True


@pytest.mark.django_db
def test_set_postage_price_without_valid_price_sets_postage_price_null(
    country, shipping_rule, order_without_shipping_price
):
    order_without_shipping_price._set_postage_price()
    order_without_shipping_price.refresh_from_db()
    assert order_without_shipping_price.postage_price is None


@pytest.mark.django_db
def test_set_postage_price_without_valid_price_sets_postage_succces_false(
    country, shipping_rule, order_without_shipping_price
):
    order_without_shipping_price._set_postage_price()
    order_without_shipping_price.refresh_from_db()
    assert order_without_shipping_price.postage_price_success is False


@pytest.mark.django_db
def test_update_postage_prices(
    country, shipping_rule, shipping_price, order_without_shipping_price
):
    models.Order.objects.update_postage_prices()
    order_without_shipping_price.refresh_from_db()
    assert order_without_shipping_price.postage_price_success is True


@pytest.mark.django_db
def test_vat_paid(order_factory, product_sale_factory):
    order = order_factory.create()
    product_sale_factory.create(order=order, price=550, quantity=1, vat_rate=20)
    product_sale_factory.create(order=order, price=550, quantity=2, vat_rate=20)
    product_sale_factory.create(order=order, price=550, quantity=1, vat_rate=0)
    assert order.vat_paid() == 274


@pytest.mark.django_db
def test_channel_fee_paid(order_factory, product_sale_factory):
    order = order_factory.create()
    product_sale_factory.create(order=order, price=550, quantity=1)
    product_sale_factory.create(order=order, price=550, quantity=2)
    assert order.channel_fee_paid() == 247


@pytest.mark.django_db
def test_purchase_price(order_factory, product_sale_factory):
    order = order_factory.create()
    product_sale_factory.create(order=order, purchase_price=550, quantity=1)
    product_sale_factory.create(order=order, purchase_price=550, quantity=2)
    assert order.purchase_price() == 1650


@pytest.mark.django_db
def test_profit(order_factory, product_sale_factory):
    order = order_factory.create(total_paid_GBP=3500, postage_price=500)
    product_sale_factory.create(
        order=order, purchase_price=550, price=550, quantity=1, vat_rate=20
    )
    product_sale_factory.create(
        order=order, purchase_price=550, price=550, quantity=2, vat_rate=20
    )
    product_sale_factory.create(
        order=order, purchase_price=550, price=550, quantity=1, vat_rate=0
    )
    assert order.profit() == 197


@pytest.mark.django_db
def test_profit_percentage(order_factory, product_sale_factory):
    order = order_factory.create(total_paid_GBP=3500, postage_price=500)
    product_sale_factory.create(
        order=order, purchase_price=550, price=550, quantity=1, vat_rate=20
    )
    product_sale_factory.create(
        order=order, purchase_price=550, price=550, quantity=2, vat_rate=20
    )
    product_sale_factory.create(
        order=order, purchase_price=550, price=550, quantity=1, vat_rate=0
    )
    assert order.profit_percentage() == 5


@pytest.mark.django_db
def test_item_count(order_factory, product_sale_factory):
    order = order_factory.create()
    product_sale_factory.create(order=order, quantity=1)
    product_sale_factory.create(order=order, quantity=3)
    assert order.item_count() == 4


@pytest.mark.django_db
def test_department(order_factory, product_sale_factory, department_factory):
    order = order_factory.create()
    department = department_factory.create()
    product_sale_factory.create(order=order, department=department)
    product_sale_factory.create(order=order, department=department)
    assert order.department() == department.name


@pytest.mark.django_db
def test_mixed_department(order_factory, product_sale_factory, department_factory):
    order = order_factory.create()
    product_sale_factory.create(order=order, department=department_factory.create())
    product_sale_factory.create(order=order, department=department_factory.create())
    assert order.department() == "Mixed"


@pytest.mark.django_db
def test_missing_department(order_factory, product_sale_factory, department_factory):
    order = order_factory.create()
    product_sale_factory.create(order=order, department=department_factory.create())
    product_sale_factory.create(order=order, department=None)
    assert order.department() is None


@pytest.mark.parametrize(
    "postage_price, details,expected",
    [
        (True, True, True),
        (False, True, True),
        (True, False, True),
        (None, True, False),
        (None, False, False),
        (True, None, False),
        (False, None, False),
    ],
)
@pytest.mark.django_db
def test_up_to_date_details(
    postage_price, details, expected, order_factory, product_sale_factory
):
    order = order_factory.create(postage_price_success=postage_price)
    product_sale_factory.create(order=order, details_success=details)
    assert order.up_to_date_details() is expected


@pytest.mark.django_db
def test_up_to_date_details_with_mixed_product_details(
    order_factory, product_sale_factory
):
    order = order_factory.create(postage_price_success=True)
    product_sale_factory.create(order=order, details_success=None)
    product_sale_factory.create(order=order, details_success=True)
    assert order.up_to_date_details() is False


@pytest.mark.parametrize(
    "postage_price, details,expected",
    [
        (True, True, True),
        (False, True, False),
        (True, False, False),
        (None, True, False),
        (None, False, False),
        (True, None, False),
        (False, None, False),
    ],
)
@pytest.mark.django_db
def test_profit_calculable_method(
    postage_price, details, expected, order_factory, product_sale_factory
):
    order = order_factory.create(postage_price_success=postage_price)
    product_sale_factory.create(order=order, details_success=details)
    assert order.profit_calculable() is expected


@pytest.mark.django_db
def test_profit_calculable_method_with_mixed_product_details(
    order_factory, product_sale_factory
):
    order = order_factory.create(postage_price_success=True)
    product_sale_factory.create(order=order, details_success=None)
    product_sale_factory.create(order=order, details_success=True)
    assert order.profit_calculable() is False
