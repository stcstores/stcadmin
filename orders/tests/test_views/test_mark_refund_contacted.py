import pytest


@pytest.fixture
def refund(
    breakage_refund_factory,
    product_sale_factory,
    packing_record_factory,
    product_refund_factory,
):
    refund = breakage_refund_factory.create(contact_contacted=False)
    product = product_sale_factory.create(order=refund.order)
    product_refund_factory.create(refund=refund, product=product)
    return refund


@pytest.fixture
def url(db, refund):
    return f"/orders/refund/{refund.id}/mark_contacted/"


@pytest.fixture
def valid_get_response(valid_get_request, url):
    return valid_get_request(url)


@pytest.fixture
def valid_get_response_content(url, valid_get_request):
    return valid_get_request(url).content.decode("utf8")


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


def test_redirects(valid_get_response, refund):
    assert valid_get_response.url == refund.get_absolute_url()


def test_marks_contacted(valid_get_response, refund):
    refund.refresh_from_db()
    assert refund.contact_contacted is True
