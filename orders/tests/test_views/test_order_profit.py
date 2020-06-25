import pytest
from pytest_django.asserts import assertTemplateUsed


@pytest.fixture
def order(order_factory):
    return order_factory.create()


@pytest.fixture
def sales(product_sale_factory, order):
    return [product_sale_factory.create(order=order) for i in range(3)]


@pytest.fixture
def url(order):
    return f"/orders/order_profit/{order.id}/"


@pytest.fixture
def valid_get_response(valid_get_request, url):
    return valid_get_request(url)


@pytest.mark.django_db
def test_logged_in_get(url, logged_in_client):
    response = logged_in_client.get(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_logged_out_get(client, url):
    response = client.get(url)
    assert response.status_code == 302


@pytest.mark.django_db
def test_logged_in_group_get(group_logged_in_client, url):
    response = group_logged_in_client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_logged_in_post(url, logged_in_client):
    response = logged_in_client.post(url)
    assert response.status_code == 403


@pytest.mark.django_db
def test_logged_out_post(client, url):
    response = client.post(url)
    assert response.status_code == 302


@pytest.mark.django_db
def test_logged_in_group_post(group_logged_in_client, url):
    response = group_logged_in_client.post(url)
    assert response.status_code == 405


@pytest.mark.django_db
def test_uses_template(valid_get_response):
    assert (
        assertTemplateUsed(valid_get_response, "orders/order_profit.html") is not False
    )


@pytest.mark.django_db
def test_order_in_context(valid_get_response, order):
    assert valid_get_response.context["order"] == order


@pytest.mark.django_db
def test_sales_in_context(sales, valid_get_response):
    assert list(valid_get_response.context["products"]) == sales
