import pytest


@pytest.fixture
def refund(
    refund_factory, product_sale_factory, packing_record_factory, product_refund_factory
):
    refund = refund_factory.create(contact_contacted=True, refund_accepted=None)
    product = product_sale_factory.create(order=refund.order)
    product_refund_factory.create(refund=refund, product=product)
    return refund


@pytest.fixture
def url(db, refund):
    return f"/orders/refund/{refund.id}/mark_rejected/"


@pytest.fixture
def valid_get_response(valid_get_request, url):
    return valid_get_request(url)


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
    assert response.status_code == 302


@pytest.mark.django_db
def test_redirects(refund, valid_get_response):
    assert valid_get_response.url == refund.get_absolute_url()


@pytest.mark.django_db
def test_marks_accepted(refund, valid_get_response):
    refund.refresh_from_db()
    assert refund.refund_accepted is False
