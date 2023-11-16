from unittest import mock

import pytest
from django.urls import reverse


@pytest.fixture
def old_quantity():
    return 3


@pytest.fixture
def new_quantity():
    return 5


@pytest.fixture
def purchase(product_purchase_factory, old_quantity):
    return product_purchase_factory.create(quantity=old_quantity, export=None)


@pytest.fixture
def completed_purchase(product_purchase_factory):
    return product_purchase_factory.create()


@pytest.fixture
def new_purchase_url(purchase):
    return reverse("purchases:update_purchase", kwargs={"pk": purchase.id})


@pytest.fixture
def completed_purchase_url(completed_purchase):
    return reverse("purchases:update_purchase", kwargs={"pk": completed_purchase.id})


@pytest.fixture
def form_data(new_quantity):
    return {"quantity": new_quantity}


@pytest.fixture
def mock_update_stock_level():
    with mock.patch(
        "purchases.views.UpdatePurchase.update_stock_level"
    ) as mock_update_stock_level:
        yield mock_update_stock_level


@pytest.fixture
def get_response(group_logged_in_client, new_purchase_url):
    return group_logged_in_client.get(new_purchase_url)


@pytest.fixture
def post_response(group_logged_in_client, new_purchase_url, form_data):
    return group_logged_in_client.post(new_purchase_url, form_data)


@pytest.mark.django_db
def test_uses_template(get_response):
    assert "purchases/update_purchase.html" in (t.name for t in get_response.templates)


@pytest.mark.django_db
def test_get_initial(old_quantity, get_response):
    form = get_response.context["form"]
    assert form.initial == {"quantity": old_quantity}


@pytest.mark.django_db
def test_post_updates_purchase(
    mock_update_stock_level, purchase, new_quantity, post_response
):
    purchase.refresh_from_db()
    assert purchase.quantity == new_quantity


@pytest.mark.django_db
def test_post_calls_update_stock_level(
    mock_update_stock_level, purchase, post_response
):
    mock_update_stock_level.assert_called_once()


@pytest.mark.django_db
def test_success_url(mock_update_stock_level, purchase, post_response):
    assert post_response["location"] == reverse(
        "purchases:manage_user_purchases", kwargs={"staff_pk": purchase.purchased_by.id}
    )


@pytest.mark.django_db
def test_get_request_for_completed_purchase_returns_404(
    group_logged_in_client, completed_purchase_url
):
    response = group_logged_in_client.get(completed_purchase_url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_post_request_for_completed_purchase_returns_404(
    mock_update_stock_level, group_logged_in_client, form_data, completed_purchase_url
):
    response = group_logged_in_client.post(completed_purchase_url, form_data)
    assert response.status_code == 404
