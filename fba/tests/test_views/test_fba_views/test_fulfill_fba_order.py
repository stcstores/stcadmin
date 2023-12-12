from unittest import mock

import pytest
from django.urls import reverse

from fba.forms import FulfillFBAOrderForm
from fba.models import FBAOrder
from fba.views.fba import FulfillFBAOrder


def test_template_name_attribute():
    assert FulfillFBAOrder.template_name == "fba/fulfill_fba_order.html"


def test_model_attribute():
    assert FulfillFBAOrder.model == FBAOrder


def test_form_class_attribute():
    assert FulfillFBAOrder.form_class == FulfillFBAOrderForm


@pytest.fixture
def mock_stock_manager():
    with mock.patch("fba.views.fba.StockManager") as m:
        m.get_stock_level.return_value = 10
        yield m


@pytest.fixture
def order(fba_order_factory):
    return fba_order_factory.create(
        status_printed=True,
        selling_price=2250,
        region__auto_close=True,
    )


@pytest.fixture
def bays(order, product_bay_link_factory):
    links = product_bay_link_factory.create_batch(3, product=order.product)
    return [link.bay for link in links]


@pytest.fixture
def mock_messages():
    with mock.patch("fba.views.fba.messages") as m:
        yield m


@pytest.fixture
def url(order, mock_stock_manager, mock_messages):
    return reverse("fba:fulfill_fba_order", args=[order.pk])


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


def test_uses_template(get_response):
    assert "fba/fulfill_fba_order.html" in (t.name for t in get_response.templates)


def test_status_code(get_response):
    assert get_response.status_code == 200


def test_request_without_group(logged_in_client, url):
    assert logged_in_client.get(url).status_code == 403


def test_form_in_context(get_response):
    assert isinstance(get_response.context["form"], FulfillFBAOrderForm)


@pytest.mark.django_db
def test_bays_in_context(bays, get_response):
    for bay in bays:
        assert bay.name in get_response.context["bays"]


def test_selling_price_in_context(get_response):
    assert get_response.context["selling_price"] == "22.50"


@pytest.fixture
def fba_packer(staff_factory):
    return staff_factory.create(fba_packer=True)


@pytest.fixture
def form_data(fba_packer):
    return {
        "box_weight": 12,
        "quantity_sent": 50,
        "fulfilled_by": fba_packer.id,
        "update_stock_level_when_complete": True,
        "notes": "Some Text",
    }


@pytest.fixture
def post_response(form_data, group_logged_in_client, url):
    return group_logged_in_client.post(url, form_data)


@pytest.mark.django_db
def test_redirects(post_response, order):
    assert post_response.status_code == 302
    assert post_response["location"] == order.get_fulfillment_url()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "auto_close,was_complete,completed,collection_booked,is_closed",
    (
        (True, True, True, False, False),
        (False, True, True, False, False),
        (True, False, True, False, True),
        (False, False, True, False, False),
        (True, True, True, True, True),
        (False, True, True, True, True),
        (True, False, True, True, True),
        (False, False, True, True, False),
        (True, True, False, False, False),
        (False, True, False, False, False),
        (True, False, False, False, False),
        (False, False, False, False, False),
        (True, True, False, True, False),
        (False, True, False, True, False),
        (True, False, False, True, False),
        (False, False, False, True, False),
    ),
)
def test_order_closed(
    auto_close,
    was_complete,
    completed,
    collection_booked,
    is_closed,
    order,
    group_logged_in_client,
    url,
    form_data,
):
    if was_complete:
        order.box_weight = 10
        order.quantity_sent = 5
    if not completed:
        form_data["box_weight"] = ""
    order.save()
    order.region.auto_close = auto_close
    order.region.save()
    if collection_booked:
        form_data["collection_booked"] = True
    group_logged_in_client.post(url, form_data)
    order.refresh_from_db()
    assert bool(order.closed_at) is is_closed


@pytest.mark.django_db
@pytest.mark.parametrize(
    "auto_close,was_complete,completed,collection_booked,stock_updated",
    (
        (True, True, True, False, False),
        (False, True, True, False, False),
        (True, False, True, False, True),
        (False, False, True, False, True),
        (True, True, True, True, False),
        (False, True, True, True, False),
        (True, False, True, True, True),
        (False, False, True, True, True),
        (True, True, False, False, False),
        (False, True, False, False, False),
        (True, False, False, False, False),
        (False, False, False, False, False),
        (True, True, False, True, False),
        (False, True, False, True, False),
        (True, False, False, True, False),
        (False, False, False, True, False),
    ),
)
def test_stock_updated(
    auto_close,
    was_complete,
    completed,
    collection_booked,
    stock_updated,
    order,
    group_logged_in_client,
    url,
    form_data,
    mock_stock_manager,
):
    if was_complete:
        order.box_weight = 10
        order.quantity_sent = 5
    if not completed:
        form_data["box_weight"] = ""
    order.save()
    order.region.auto_close = auto_close
    order.region.save()
    if collection_booked:
        form_data["collection_booked"] = True
    group_logged_in_client.post(url, form_data)
    order.refresh_from_db()
    if stock_updated:
        mock_stock_manager.set_stock_level.assert_called_once()
    else:
        mock_stock_manager.set_stock_level.assert_not_called()


@pytest.mark.django_db
def test_update_stock(mock_stock_manager, order, user, post_response):
    order.refresh_from_db()
    mock_stock_manager.get_stock_level.assert_called_once_with(order.product)
    mock_stock_manager.set_stock_level.assert_called_once_with(
        product=order.product,
        user=user,
        new_stock_level=mock_stock_manager.get_stock_level.return_value
        - order.quantity_sent,
        change_source=f"Updated by FBA order pk={order.pk}",
    )


def test_fulfill_order(mock_messages):
    view = FulfillFBAOrder()
    view.update_stock = mock.Mock()
    view.object = mock.Mock()
    view.request = mock.Mock()
    view.fulfill_order()
    view.update_stock.assert_called_once_with()
    mock_messages.add_message.assert_called_once_with(
        view.request,
        mock_messages.SUCCESS,
        f"FBA order fulfilled for product {view.object.product.sku}.",
    )


def test_close_order(mock_messages):
    view = FulfillFBAOrder()
    view.object = mock.Mock()
    view.request = mock.Mock()
    view.close_order()
    view.object.close.assert_called_once_with()
    mock_messages.add_message.assert_called_once_with(
        view.request,
        mock_messages.SUCCESS,
        f"FBA order closed for product {view.object.product.sku}.",
    )


def test_update_stock_in_debug(settings, mock_messages, mock_stock_manager):
    settings.DEBUG = True
    view = FulfillFBAOrder()
    view.request = mock.Mock()
    view._update_stock = mock.Mock()
    view.update_stock()
    view._update_stock.assert_not_called()
    mock_messages.add_message.assert_called_once_with(
        view.request, mock_messages.WARNING, "Stock update skipped: DEBUG mode."
    )


def test_update_stock_with_update_when_complete_false(
    mock_messages, mock_stock_manager
):
    view = FulfillFBAOrder()
    view.request = mock.Mock()
    view.object = mock.Mock()
    view.object.update_stock_level_when_complete = False
    view._update_stock = mock.Mock()
    view.update_stock()
    view._update_stock.assert_not_called()
    mock_messages.add_message.assert_called_once_with(
        view.request,
        mock_messages.WARNING,
        (
            f"Set to skip stock update, the stock level for {view.object.product.sku} "
            "is unchanged."
        ),
    )


def test_update_stock_with_update_when_complete_true(mock_messages, mock_stock_manager):
    view = FulfillFBAOrder()
    view.request = mock.Mock()
    view.object = mock.Mock()
    view.object.update_stock_level_when_complete = True
    view._update_stock = mock.Mock(return_value=(5, 10))
    view.update_stock()
    view._update_stock.assert_called_once_with()
    mock_messages.add_message.assert_called_once_with(
        view.request,
        mock_messages.SUCCESS,
        f"Changed stock level for {view.object.product.sku} from 5 to 10",
    )


def test_update_stock_with_update_with_error(mock_messages, mock_stock_manager):
    view = FulfillFBAOrder()
    view.request = mock.Mock()
    view.object = mock.Mock()
    view.object.update_stock_level_when_complete = True
    view._update_stock = mock.Mock(side_effect=Exception)
    view.update_stock()
    view._update_stock.assert_called_once_with()
    mock_messages.add_message.assert_called_once_with(
        view.request,
        mock_messages.ERROR,
        (
            f"Stock Level failed to update for {view.object.product.sku}, "
            "please check stock level."
        ),
    )
