import pytest

from feedback.models import Feedback, UserFeedback


@pytest.fixture
def refund(
    packing_mistake_refund_factory, product_sale_factory, product_refund_factory,
):
    refund = packing_mistake_refund_factory.create()
    product = product_sale_factory.create(order=refund.order)
    product_refund_factory.create(refund=refund, product=product)
    return refund


@pytest.fixture
def packing_record(packing_record_factory, refund):
    return packing_record_factory.create(order=refund.order)


@pytest.fixture
def feedback_type():
    Feedback.objects.create(name="Packing Mistake")


@pytest.fixture
def url(db, refund, packing_record, feedback_type):
    return f"/orders/refund/{refund.id}/create_feedback/"


@pytest.fixture
def valid_get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


def test_logged_in_get(url, logged_in_client):
    response = logged_in_client.get(url)
    assert response.status_code == 403


def test_logged_out_get(client, url):
    response = client.get(url)
    assert response.status_code == 302


def test_logged_in_group_get(group_logged_in_client, url):
    response = group_logged_in_client.get(url)
    assert response.status_code == 302


def test_logged_in_post(url, logged_in_client):
    response = logged_in_client.post(url)
    assert response.status_code == 403


def test_logged_out_post(client, url):
    response = client.post(url)
    assert response.status_code == 302


def test_logged_in_group_post(group_logged_in_client, url):
    response = group_logged_in_client.post(url)
    assert response.status_code == 404


def test_redirects(valid_get_response, refund):
    assert valid_get_response.url == refund.get_absolute_url()


def test_creates_feedback(valid_get_response, refund, packing_record):
    assert UserFeedback.objects.filter(
        order_id=refund.order.order_ID,
        feedback_type__name="Packing Mistake",
        user=packing_record.packed_by,
    )
