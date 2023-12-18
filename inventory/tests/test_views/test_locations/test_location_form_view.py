from unittest import mock

import pytest
from django.contrib import messages
from django.urls import reverse

from inventory import forms
from inventory.views.locations import LocationFormView


@pytest.fixture
def product_range(product_range_factory):
    return product_range_factory.create()


@pytest.fixture
def products(product_range, product_factory):
    return product_factory.create_batch(3, product_range=product_range)


@pytest.fixture
def url(product_range):
    return reverse("inventory:locations", kwargs={"range_pk": product_range.pk})


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.fixture(autouse=True)
def mock_stock_manager():
    with mock.patch("inventory.views.locations.StockManager") as mock_stock_manager:
        yield mock_stock_manager


@pytest.mark.django_db
def test_uses_template(get_response):
    assert "inventory/product_range/locations.html" in [
        t.name for t in get_response.templates
    ]


@pytest.mark.django_db
def test_get_initial(
    group_logged_in_client,
    url,
    product_range,
    product_factory,
    bay_factory,
    product_bay_link_factory,
):
    products = product_factory.create_batch(3, product_range=product_range)
    bays = bay_factory.create_batch(3)
    for product, bay in zip(products, bays):
        product_bay_link_factory.create(product=product, bay=bay)
    response = group_logged_in_client.get(url)
    initial = response.context["form"].initial
    assert initial == [
        {"product_id": products[i].id, "bays": [bays[i].id]} for i in range(3)
    ]


@pytest.mark.django_db
def test_product_range_in_context(product_range, get_response):
    assert get_response.context["product_range"] == product_range


@pytest.mark.django_db
def test_formset_in_context(products, get_response):
    formset = get_response.context["formset"]
    assert isinstance(formset, forms.LocationsFormSet)
    assert len(formset) == 3
    for i in range(3):
        assert formset[i].product == products[i]


@pytest.mark.django_db
def test_products_exist_in_context(products, mock_stock_manager, get_response):
    products_exist = get_response.context["products_exist"]
    assert products_exist == mock_stock_manager.products_exist.return_value
    mock_stock_manager.products_exist.assert_called_once_with(
        *[product.sku for product in products]
    )


@pytest.mark.django_db
def test_ignores_errors_checking_products_exist(
    products, mock_stock_manager, group_logged_in_client, url
):
    mock_stock_manager.products_exist.side_effect = Exception
    response = group_logged_in_client.get(url)
    assert response.context["products_exist"] is None


@pytest.mark.django_db
def test_does_not_check_proudcts_exist_when_product_range_is_eol(
    mock_stock_manager, product_range, group_logged_in_client, url
):
    product_range.is_end_of_line = True
    product_range.save()
    response = group_logged_in_client.get(url)
    assert response.context["products_exist"] is None
    mock_stock_manager.products_exist.assert_not_called()


@pytest.mark.django_db
def test_form_valid_calls_save_on_forms(user_factory, product_range):
    user = user_factory.create()
    formset = [mock.Mock(), mock.Mock(), mock.Mock()]
    view = LocationFormView()
    view.product_range = product_range
    view.request = mock.Mock(user=user)
    view.form_valid(formset)
    for form in formset:
        form.save.assert_called_once_with(user=user)


@pytest.mark.django_db
def test_form_valid_adds_message(group_logged_in_client, url):
    with mock.patch(
        "inventory.views.locations.LocationsFormSet.is_valid",
        mock.Mock(return_value=True),
    ):
        response = group_logged_in_client.post(url, {}, follow=True)
    message = list(response.context["messages"])[0]
    assert message.message == "Locations Updated"
    assert message.level == messages.SUCCESS
