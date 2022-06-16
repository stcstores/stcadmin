import pytest


@pytest.fixture
def refund(
    breakage_refund_factory,
    product_sale_factory,
    product_refund_factory,
):
    refund = breakage_refund_factory.create(
        contact_contacted=True, refund_accepted=None
    )
    product = product_sale_factory.create(order=refund.order)
    product_refund_factory.create(refund=refund, product=product)
    return refund


@pytest.fixture
def url(db, refund):
    return f"/orders/refund/{refund.id}/mark_accepted/"


@pytest.fixture
def valid_get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url, {"refund_amount": "5.78"})


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
    response = group_logged_in_client.get(url, {"refund_amount": "5.78"})
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


def test_marks_accepted(valid_get_response, refund):
    refund.refresh_from_db()
    assert refund.refund_accepted is True


def test_sets_refund_amount(valid_get_response, refund):
    refund.refresh_from_db()
    assert refund.refund_amount == 578
