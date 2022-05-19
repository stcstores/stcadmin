from datetime import datetime
from unittest.mock import patch

import pytest
from django.utils import timezone

from orders import models


@pytest.fixture
def order_id():
    return "38839822"


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
def external_reference():
    return "384048338BK"


@pytest.fixture
def country(country_factory):
    return country_factory.create()


@pytest.fixture
def shipping_service(shipping_service_factory):
    return shipping_service_factory.create()


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
def new_order(order_id, recieved_at, channel, country, shipping_service):
    new_order = models.Order(
        order_id=order_id,
        recieved_at=recieved_at,
        country=country,
        shipping_service=shipping_service,
    )
    new_order.save()
    return new_order


@pytest.mark.django_db
def test_sets_order_id(new_order, order_id):
    assert new_order.order_id == order_id


@pytest.mark.django_db
def test_sets_recieved_at(new_order, recieved_at):
    assert new_order.recieved_at == recieved_at


@pytest.mark.django_db
def test_dispatched_at_defaults_to_None(new_order):
    assert new_order.dispatched_at is None


@pytest.mark.django_db
def test_can_set_dispatched_at(
    order_id, recieved_at, country, shipping_service, dispatched_at
):
    order = models.Order(
        order_id=order_id,
        recieved_at=recieved_at,
        country=country,
        shipping_service=shipping_service,
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
def test_can_set_channel(order_id, recieved_at, country, shipping_service, channel):
    order = models.Order(
        order_id=order_id,
        recieved_at=recieved_at,
        country=country,
        shipping_service=shipping_service,
        channel=channel,
    )
    order.save()
    order.refresh_from_db()
    assert order.channel == channel


@pytest.mark.django_db
def test_external_reference_defaults_to_None(new_order):
    assert new_order.external_reference is None


@pytest.mark.django_db
def test_can_set_external_reference(
    order_id, recieved_at, country, shipping_service, external_reference
):
    order = models.Order(
        order_id=order_id,
        recieved_at=recieved_at,
        country=country,
        shipping_service=shipping_service,
        external_reference=external_reference,
    )
    order.save()
    order.refresh_from_db()
    assert order.external_reference == external_reference


@pytest.mark.django_db
def test_sets_country(new_order, country):
    assert new_order.country == country


@pytest.mark.django_db
def test_sets_shipping_service(new_order, shipping_service):
    assert new_order.shipping_service == shipping_service


@pytest.mark.django_db
def test_tracking_number_defaults_to_None(new_order):
    assert new_order.tracking_number is None


@pytest.mark.django_db
def test_can_set_tracking_number(
    order_id, recieved_at, country, shipping_service, tracking_number
):
    order = models.Order(
        order_id=order_id,
        recieved_at=recieved_at,
        country=country,
        shipping_service=shipping_service,
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
    order_id, recieved_at, country, shipping_service, total_paid
):
    order = models.Order(
        order_id=order_id,
        recieved_at=recieved_at,
        country=country,
        shipping_service=shipping_service,
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
    order_id, recieved_at, country, shipping_service, total_paid_GBP
):
    order = models.Order(
        order_id=order_id,
        recieved_at=recieved_at,
        country=country,
        shipping_service=shipping_service,
        total_paid_GBP=total_paid_GBP,
    )
    order.save()
    order.refresh_from_db()
    assert order.total_paid_GBP == total_paid_GBP


@pytest.mark.django_db
def test__str__method(order_factory):
    order = order_factory.create(order_id="3849383")
    assert str(order) == "Order: 3849383"


def test_is_dispatched_returns_true_if_order_is_dispatched(
    order_factory, dispatched_at
):
    order = order_factory.build(dispatched_at=dispatched_at)
    assert order.is_dispatched() is True


def test_is_dispatched_returns_false_if_order_is_not_dispatched(order_factory):
    order = order_factory.build(dispatched_at=None)
    assert order.is_dispatched() is False


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
        ({"shipping_service__priority": True, "cancelled": False}, True),
        ({"shipping_service__priority": True, "cancelled": True}, False),
        ({"shipping_service__priority": False, "cancelled": True}, False),
        ({"shipping_service__priority": False, "cancelled": False}, False),
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
        ({"shipping_service__priority": True, "cancelled": False}, False),
        ({"shipping_service__priority": True, "cancelled": True}, False),
        ({"shipping_service__priority": False, "cancelled": True}, False),
        ({"shipping_service__priority": False, "cancelled": False}, True),
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


@pytest.fixture
def shipping_price(country, shipping_price_factory):
    return shipping_price_factory.create(country=country)


@pytest.fixture
def order_without_shipping_price(country, order_factory):
    return order_factory.create(
        country=country,
        postage_price=None,
        postage_price_success=None,
    )


@pytest.mark.django_db
def test_channel_fee_paid(order_factory, product_sale_factory):
    order = order_factory.create()
    product_sale_factory.create(order=order, price=550, quantity=1)
    product_sale_factory.create(order=order, price=550, quantity=2)
    assert order.channel_fee_paid() == 255


@pytest.mark.django_db
def test_purchase_price(order_factory, product_sale_factory):
    order = order_factory.create()
    product_sale_factory.create(order=order, purchase_price=550, quantity=1)
    product_sale_factory.create(order=order, purchase_price=550, quantity=2)
    assert order.purchase_price() == 1650


@pytest.mark.django_db
def test_item_count(order_factory, product_sale_factory):
    order = order_factory.create()
    product_sale_factory.create(order=order, quantity=1)
    product_sale_factory.create(order=order, quantity=3)
    assert order.item_count() == 4


@pytest.fixture
def mock_set_postage_price():
    with patch(
        "orders.models.order.Order._set_postage_price"
    ) as mock_set_posrage_price:
        yield mock_set_posrage_price


@pytest.mark.django_db
def test_set_postage_price_error(mock_set_postage_price, order_without_shipping_price):
    mock_set_postage_price.side_effect = Exception("exception message")
    order_id = order_without_shipping_price.order_id
    with pytest.raises(Exception) as excinfo:
        models.Order.objects.update_postage_prices()
    assert (
        f"Error finding postage price for order {order_id}: exception message"
        in str(excinfo)
    )


# @pytest.mark.django_db
# def test_get_postage_price(country, shipping_price, order_factory):
#     order = order_factory.create(
#         country=country,
#     )
#     assert order._get_postage_price() == shipping_price.price(order.total_weight())


# @pytest.mark.django_db
# def test_set_postage_price_sets_postage_price(country, shipping_price, order_factory):
#     order = order_factory.create(
#         country=country,
#         postage_price=None,
#         postage_price_success=None,
#     )
#     order._set_postage_price()
#     order.refresh_from_db()
#     assert order.postage_price == shipping_price.price(order.total_weight())


# @pytest.mark.django_db
# def test_set_postage_price_does_not_stop_for_missing_weight_band(
#     country,
#     shipping_price,
#     order_factory,
#     weight_band_factory,
#     product_sale_factory,
# ):
#     weight_band_factory.create(
#         min_weight=0, max_weight=20, shipping_price=shipping_price
#     )
#     order = order_factory.create(
#         country=country,
#         postage_price=None,
#         postage_price_success=None,
#     )
#     product_sale_factory.create(order=order, weight=500)
#     order._set_postage_price()
#     assert order.postage_price is None
#     assert order.postage_price_success is False


# @pytest.mark.django_db
# def test_set_postage_price_sets_postage_price_success(
#     country, shipping_price, order_without_shipping_price
# ):
#     order_without_shipping_price._set_postage_price()
#     order_without_shipping_price.refresh_from_db()
#     assert order_without_shipping_price.postage_price_success is True


# @pytest.mark.django_db
# def test_set_postage_price_without_valid_price_sets_postage_price_null(
#     country, order_without_shipping_price
# ):
#     order_without_shipping_price._set_postage_price()
#     order_without_shipping_price.refresh_from_db()
#     assert order_without_shipping_price.postage_price is None


# @pytest.mark.django_db
# def test_set_postage_price_without_valid_price_sets_postage_succces_false(
#     country, order_without_shipping_price
# ):
#     order_without_shipping_price._set_postage_price()
#     order_without_shipping_price.refresh_from_db()
#     assert order_without_shipping_price.postage_price_success is False


# @pytest.mark.django_db
# def test_update_postage_prices(country, shipping_price, order_without_shipping_price):
#     models.Order.objects.update_postage_prices()
#     order_without_shipping_price.refresh_from_db()
#     assert order_without_shipping_price.postage_price_success is True


# @pytest.mark.django_db
# def test_vat_paid(order_factory, product_sale_factory):
#     order = order_factory.create(country__vat_required=Country.VAT_VARIABLE)
#     product_sale_factory.create(order=order, price=550, quantity=1, vat=20)
#     product_sale_factory.create(order=order, price=550, quantity=2, vat=20)
#     product_sale_factory.create(order=order, price=550, quantity=1, vat=0)
#     assert order.vat_paid() == 274


# @pytest.mark.django_db
# def test_postage_price_success_is_false_if_total_paid_is_zero(
#     country, shipping_price, order_factory
# ):
#     order = order_factory.create(
#         total_paid=0,
#         country=country,
#         postage_price=None,
#         postage_price_success=None,
#     )
#     models.Order.objects.update_postage_prices()
#     order.refresh_from_db()
#     assert order.postage_price_success is False


# @pytest.mark.django_db
# def test_postage_price_success_is_false_if_total_paid_GBP_is_zero(
#     country, shipping_price, order_factory
# ):
#     order = order_factory.create(
#         total_paid_GBP=0,
#         country=country,
#         postage_price=None,
#         postage_price_success=None,
#     )
#     models.Order.objects.update_postage_prices()
#     order.refresh_from_db()
#     assert order.postage_price_success is False


# @pytest.mark.django_db
# def test_vat_paid_returns_zero_if_vat_not_required(order_factory, product_sale_factory):
#     order = order_factory.create(country__vat_required=Country.VAT_NEVER)
#     product_sale_factory.create(order=order, price=550, quantity=1, vat=20)
#     product_sale_factory.create(order=order, price=550, quantity=2, vat=20)
#     product_sale_factory.create(order=order, price=550, quantity=1, vat=0)
#     assert order.vat_paid() == 0


# @pytest.mark.django_db
# def test_profit(order_factory, product_sale_factory):
#     order = order_factory.create(total_paid_GBP=3500, postage_price=500)
#     product_sale_factory.create(
#         order=order, purchase_price=550, price=550, quantity=1, vat=20
#     )
#     product_sale_factory.create(
#         order=order, purchase_price=550, price=550, quantity=2, vat=20
#     )
#     product_sale_factory.create(
#         order=order, purchase_price=550, price=550, quantity=1, vat=0
#     )
#     assert order.profit() == 186


# @pytest.mark.django_db
# def test_profit_percentage(order_factory, product_sale_factory):
#     order = order_factory.create(total_paid_GBP=3500, postage_price=500)
#     product_sale_factory.create(
#         order=order, purchase_price=550, price=550, quantity=1, vat=20
#     )
#     product_sale_factory.create(
#         order=order, purchase_price=550, price=550, quantity=2, vat=20
#     )
#     product_sale_factory.create(
#         order=order, purchase_price=550, price=550, quantity=1, vat=0
#     )
#     assert order.profit_percentage() == 5
