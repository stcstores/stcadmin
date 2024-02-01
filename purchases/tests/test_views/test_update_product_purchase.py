from unittest import mock

import pytest
from django.contrib import messages
from django.test.utils import override_settings
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
    return reverse("purchases:update_product_purchase", kwargs={"pk": purchase.id})


@pytest.fixture
def completed_purchase_url(completed_purchase):
    return reverse(
        "purchases:update_product_purchase", kwargs={"pk": completed_purchase.id}
    )


@pytest.fixture
def form_data(new_quantity):
    return {"quantity": new_quantity}


@pytest.fixture
def mock_update_stock_level():
    with mock.patch(
        "purchases.views.UpdateProductPurchase.update_stock_level"
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
    assert "purchases/update_product_purchase.html" in [
        t.name for t in get_response.templates
    ]


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


@pytest.fixture
def mock_form():
    return mock.Mock()


@pytest.fixture
def mock_get_form(mock_form):
    with mock.patch("purchases.views.UpdateProductPurchase.get_form") as mock_get_form:
        mock_get_form.return_value = mock_form
        yield mock_get_form


@pytest.mark.django_db
def test_sets_success_message(
    group_logged_in_client, mock_get_form, mock_form, new_purchase_url, form_data
):
    response = group_logged_in_client.post(new_purchase_url, form_data, follow=True)
    message = list(response.context["messages"])[0]
    assert message.level == messages.SUCCESS
    mock_form.update_stock_level.assert_called_once_with()


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_sets_debug_message(
    group_logged_in_client, mock_get_form, mock_form, new_purchase_url, form_data
):
    response = group_logged_in_client.post(new_purchase_url, form_data, follow=True)
    message = list(response.context["messages"])[0]
    assert message.level == messages.WARNING
    mock_form.update_stock_level.assert_not_called()


@pytest.mark.django_db
def test_sets_error_message(
    group_logged_in_client, mock_get_form, mock_form, new_purchase_url, form_data
):
    mock_form.update_stock_level.side_effect = Exception
    response = group_logged_in_client.post(new_purchase_url, form_data, follow=True)
    message = list(response.context["messages"])[0]
    assert message.level == messages.ERROR
    mock_form.update_stock_level.assert_called_once_with()
