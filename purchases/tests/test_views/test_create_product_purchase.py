from unittest import mock

import pytest
from django.contrib import messages
from django.test.utils import override_settings
from django.urls import reverse

from home.models import Staff


@pytest.fixture
def purchase_settings(purchase_settings_factory):
    return purchase_settings_factory.create()


@pytest.fixture
def staff(staff_factory, user):
    staff_obj, _ = Staff.objects.get_or_create(stcadmin_user=user)
    return staff_obj


@pytest.fixture
def product(product_factory):
    return product_factory.create()


@pytest.fixture
def url(staff, purchase_settings, product):
    return reverse(
        "purchases:create_product_purchase", kwargs={"product_pk": product.id}
    )


@pytest.fixture
def form_data():
    return {"key": "value"}


@pytest.fixture
def mock_form():
    return mock.Mock()


@pytest.fixture
def mock_get_form(mock_form):
    with mock.patch("purchases.views.CreateProductPurchase.get_form") as mock_get_form:
        mock_get_form.return_value = mock_form
        yield mock_get_form


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.fixture
def post_response(mock_get_form, group_logged_in_client, url, form_data):
    return group_logged_in_client.post(url, form_data)


@pytest.mark.django_db
def test_uses_template(get_response):
    assert "purchases/create_product_purchase.html" in [
        t.name for t in get_response.templates
    ]


@pytest.mark.django_db
def test_get_initial(staff, product, get_response):
    form = get_response.context["form"]
    assert form.initial == {"purchaser": staff.id, "product_id": product.id}


@pytest.mark.django_db
def test_product_in_context(product, get_response):
    assert get_response.context["product"] == product


@pytest.mark.django_db
def test_to_pay_in_context(purchase_settings, product, get_response):
    expected_value = product.purchase_price * purchase_settings.purchase_charge
    assert get_response.context["to_pay"] == expected_value


@pytest.mark.django_db
def test_post_calls_form_is_valid_method(mock_form, post_response):
    mock_form.is_valid.assert_called_once_with()


@pytest.mark.django_db
def test_post_calls_form_save_method(mock_form, post_response):
    mock_form.save.assert_called_once_with()


@pytest.mark.django_db
def test_post_calls_form_udpate_stock_method(mock_form, post_response):
    mock_form.update_stock_level.assert_called_once_with()


@pytest.mark.django_db
def test_sets_success_message(
    group_logged_in_client, mock_get_form, mock_form, url, form_data
):
    response = group_logged_in_client.post(url, form_data, follow=True)
    message = list(response.context["messages"])[0]
    assert message.level == messages.SUCCESS
    mock_form.update_stock_level.assert_called_once_with()


@pytest.mark.django_db
@override_settings(DEBUG=True)
def test_sets_debug_message(
    group_logged_in_client, mock_get_form, mock_form, url, form_data
):
    response = group_logged_in_client.post(url, form_data, follow=True)
    message = list(response.context["messages"])[0]
    assert message.level == messages.WARNING
    mock_form.update_stock_level.assert_not_called()


@pytest.mark.django_db
def test_sets_error_message(
    group_logged_in_client, mock_get_form, mock_form, url, form_data
):
    mock_form.update_stock_level.side_effect = Exception
    response = group_logged_in_client.post(url, form_data, follow=True)
    message = list(response.context["messages"])[0]
    assert message.level == messages.ERROR
    mock_form.update_stock_level.assert_called_once_with()


@pytest.mark.django_db
def test_success_url(post_response):
    assert post_response["location"] == reverse("purchases:index")
