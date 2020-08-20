from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from django.utils import timezone
from pytest_django.asserts import assertTemplateUsed

from orders import views


@pytest.fixture
def url():
    return "/orders/refund_list/"


@pytest.fixture
def valid_get_response(valid_get_request, url):
    return valid_get_request(url)


@pytest.fixture
def valid_get_response_content(url, valid_get_request):
    return valid_get_request(url).content.decode("utf8")


@pytest.fixture
def refund(refund_factory):
    return refund_factory.create()


@pytest.fixture
def mock_now():
    with patch("django.utils.timezone.now") as mock_now:
        date_time = timezone.make_aware(datetime(2020, 3, 26))
        mock_now.return_value = date_time
        yield date_time


def test_logged_in_get(url, logged_in_client):
    response = logged_in_client.get(url)
    assert response.status_code == 403


def test_logged_out_get(client, url):
    response = client.get(url)
    assert response.status_code == 302


def test_logged_in_group_get(group_logged_in_client, url):
    response = group_logged_in_client.get(url)
    assert response.status_code == 200


def test_logged_in_post(url, logged_in_client):
    response = logged_in_client.post(url)
    assert response.status_code == 403


def test_logged_out_post(client, url):
    response = client.post(url)
    assert response.status_code == 302


def test_logged_in_group_post(group_logged_in_client, url):
    response = group_logged_in_client.post(url)
    assert response.status_code == 405


def test_uses_template(valid_get_response):
    assert (
        assertTemplateUsed(valid_get_response, "orders/refunds/refund_list.html")
        is not False
    )


@pytest.mark.django_db
def test_shows_order_ID(refund, valid_get_response_content):
    assert refund.order.order_ID in valid_get_response_content


@pytest.mark.django_db
def test_shows_dispatched_at(mock_now, refund, valid_get_response_content):
    assert refund.order.dispatched_at.strftime("%Y-%m-%d") in valid_get_response_content


@pytest.mark.django_db
def test_shows_department(refund, valid_get_response_content):
    assert refund.order.department() in valid_get_response_content


@pytest.mark.django_db
def test_links_to_refund_page(refund, valid_get_response_content):
    assert refund.get_absolute_url() in valid_get_response_content


@pytest.mark.django_db
def test_shows_reason(refund, valid_get_response_content):
    assert refund.reason() in valid_get_response_content


@pytest.mark.django_db
@pytest.mark.parametrize(
    "refund_kwargs,status",
    [
        ({"contact_contacted": False, "refund_accepted": None}, "Not Contacted"),
        ({"contact_contacted": True, "refund_accepted": None}, "Awaiting Response"),
        ({"contact_contacted": True, "refund_accepted": True}, "Accepted"),
        ({"contact_contacted": True, "refund_accepted": False}, "Rejected"),
    ],
)
def test_refund_status(
    refund_kwargs, status, breakage_refund_factory, url, group_logged_in_client
):
    breakage_refund_factory.create(**refund_kwargs)
    response = group_logged_in_client.get(url)
    content = response.content.decode("utf8")
    assert status in content


@pytest.mark.django_db
@pytest.mark.parametrize(
    "dispatched_at,shown",
    [
        (datetime(2019, 12, 2, 23, 59), False),
        (datetime(2019, 12, 3, 0, 0), True),
        (datetime(2019, 12, 4, 23, 59), True),
        (datetime(2019, 12, 5, 0, 0), False),
    ],
)
def test_date_filter(dispatched_at, shown, refund_factory, url, group_logged_in_client):
    refund = refund_factory.create(
        order__dispatched_at=timezone.make_aware(dispatched_at)
    )
    dispatched_from = timezone.make_aware(datetime(2019, 12, 3))
    dispatched_to = timezone.make_aware(datetime(2019, 12, 4))
    response = group_logged_in_client.get(
        url,
        {
            "dispatched_from": dispatched_from.strftime("%Y-%m-%d"),
            "dispatched_to": dispatched_to.strftime("%Y-%m-%d"),
        },
    )
    content = response.content.decode("utf8")
    assert (refund.order.order_ID in content) is shown


@pytest.mark.django_db
def test_order_ID_filter(country_factory, refund_factory, url, group_logged_in_client):
    refund = refund_factory.create()
    other_refund = refund_factory.create()
    response = group_logged_in_client.get(url, {"order_ID": refund.order.order_ID})
    content = response.content.decode("utf8")
    assert refund.order.order_ID in content
    assert other_refund.order.order_ID not in content


@pytest.mark.django_db
def test_filter_contacted_any(breakage_refund_factory, url, group_logged_in_client):
    refunds = [
        breakage_refund_factory.create(contact_contacted=True),
        breakage_refund_factory.create(contact_contacted=False),
    ]
    response = group_logged_in_client.get(url, {"contacted": "any"})
    content = response.content.decode("utf8")
    for refund in refunds:
        assert refund.order.order_ID in content


@pytest.mark.django_db
def test_filter_contacted_yes(breakage_refund_factory, url, group_logged_in_client):
    refunds = [
        breakage_refund_factory.create(contact_contacted=True),
        breakage_refund_factory.create(contact_contacted=False),
    ]
    response = group_logged_in_client.get(url, {"contacted": "yes"})
    content = response.content.decode("utf8")
    assert refunds[0].order.order_ID in content
    assert refunds[1].order.order_ID not in content


@pytest.mark.django_db
def test_filter_contacted_no(breakage_refund_factory, url, group_logged_in_client):
    refunds = [
        breakage_refund_factory.create(contact_contacted=True),
        breakage_refund_factory.create(contact_contacted=False),
    ]
    response = group_logged_in_client.get(url, {"contacted": "no"})
    content = response.content.decode("utf8")
    assert refunds[0].order.order_ID not in content
    assert refunds[1].order.order_ID in content


@pytest.mark.django_db
def test_filter_accepted_any(breakage_refund_factory, url, group_logged_in_client):
    refunds = [
        breakage_refund_factory.create(refund_accepted=True),
        breakage_refund_factory.create(refund_accepted=False),
        breakage_refund_factory.create(refund_accepted=None),
    ]
    response = group_logged_in_client.get(url, {"accepted": "any"})
    content = response.content.decode("utf8")
    for refund in refunds:
        assert refund.order.order_ID in content


@pytest.mark.django_db
def test_filter_accepted_yes(breakage_refund_factory, url, group_logged_in_client):
    refunds = [
        breakage_refund_factory.create(refund_accepted=True),
        breakage_refund_factory.create(refund_accepted=False),
        breakage_refund_factory.create(refund_accepted=None),
    ]
    response = group_logged_in_client.get(url, {"accepted": "yes"})
    content = response.content.decode("utf8")
    assert refunds[0].order.order_ID in content
    assert refunds[1].order.order_ID not in content
    assert refunds[2].order.order_ID not in content


@pytest.mark.django_db
def test_filter_accepted_no(breakage_refund_factory, url, group_logged_in_client):
    refunds = [
        breakage_refund_factory.create(refund_accepted=True),
        breakage_refund_factory.create(refund_accepted=False),
        breakage_refund_factory.create(refund_accepted=None),
    ]
    response = group_logged_in_client.get(url, {"accepted": "no"})
    content = response.content.decode("utf8")
    assert refunds[0].order.order_ID not in content
    assert refunds[1].order.order_ID in content
    assert refunds[2].order.order_ID not in content


@pytest.mark.django_db
def test_filter_closed_any(refund_factory, url, group_logged_in_client):
    refunds = [
        refund_factory.create(closed=True),
        refund_factory.create(closed=False),
    ]
    response = group_logged_in_client.get(url, {"closed": "any"})
    content = response.content.decode("utf8")
    for refund in refunds:
        assert refund.order.order_ID in content


@pytest.mark.django_db
def test_filter_closed_yes(refund_factory, url, group_logged_in_client):
    refunds = [
        refund_factory.create(closed=True),
        refund_factory.create(closed=False),
    ]
    response = group_logged_in_client.get(url, {"closed": "yes"})
    content = response.content.decode("utf8")
    assert refunds[0].order.order_ID in content
    assert refunds[1].order.order_ID not in content


@pytest.mark.django_db
def test_filter_closed_no(refund_factory, url, group_logged_in_client):
    refunds = [
        refund_factory.create(closed=True),
        refund_factory.create(closed=False),
    ]
    response = group_logged_in_client.get(url, {"closed": "no"})
    content = response.content.decode("utf8")
    assert refunds[0].order.order_ID not in content
    assert refunds[1].order.order_ID in content


@pytest.mark.django_db
def test_filter_refund_type(
    breakage_refund_factory, demic_refund_factory, url, group_logged_in_client
):
    breakage = breakage_refund_factory.create()
    demic = demic_refund_factory.create()
    response = group_logged_in_client.get(url, {"refund_type": "breakage"})
    content = response.content.decode("utf8")
    assert breakage.order.order_ID in content
    assert demic.order.order_ID not in content


def test_invalid_form(group_logged_in_client, url):
    response = group_logged_in_client.get(url, {"refund_type": "INVALID"})
    assert response.status_code == 200
    assert "refund_type" in response.context["form"].errors


def test_page_range():
    paginator = Mock(num_pages=5)
    paginator.num_pages = 55
    page_numbers = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 55]
    assert views.RefundList().get_page_range(paginator) == page_numbers


@pytest.mark.django_db
def test_search_by_sku(
    breakage_refund_factory, product_refund_factory, url, group_logged_in_client
):
    refund = breakage_refund_factory.create()
    product_refund_factory.create(refund=refund, product__sku="ABC-123-DEF")
    other_refund = breakage_refund_factory.create()
    product_refund_factory.create(refund=other_refund, product__sku="999-KFR-232")
    response = group_logged_in_client.get(url, {"search": "abc"})
    assert list(response.context["object_list"]) == [refund]


@pytest.mark.django_db
def test_search_by_name(
    breakage_refund_factory, product_refund_factory, url, group_logged_in_client
):
    refund = breakage_refund_factory.create()
    product_refund_factory.create(refund=refund, product__name="French Bulldog")
    other_refund = breakage_refund_factory.create()
    product_refund_factory.create(refund=other_refund, product__name="Other Product")
    response = group_logged_in_client.get(url, {"search": "bulldog"})
    assert list(response.context["object_list"]) == [refund]


@pytest.mark.django_db
def test_search_by_supplier(
    breakage_refund_factory, product_refund_factory, url, group_logged_in_client
):
    refund = breakage_refund_factory.create()
    product_refund_factory.create(refund=refund, product__supplier__name="Nemesis")
    other_refund = breakage_refund_factory.create()
    product_refund_factory.create(
        refund=other_refund, product__supplier__name="Other Supplier"
    )
    response = group_logged_in_client.get(url, {"search": "neme"})
    assert list(response.context["object_list"]) == [refund]


@pytest.mark.django_db
def test_supplier_filter(
    breakage_refund_factory, product_refund_factory, url, group_logged_in_client
):
    refund = breakage_refund_factory.create()
    product = product_refund_factory.create(refund=refund)
    other_refund = breakage_refund_factory.create()
    product_refund_factory.create(refund=other_refund)
    response = group_logged_in_client.get(
        url, {"supplier": product.product.supplier.id}
    )
    assert list(response.context["object_list"]) == [refund]
