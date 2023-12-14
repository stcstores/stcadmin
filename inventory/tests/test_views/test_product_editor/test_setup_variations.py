import json
from unittest import mock

import pytest
from django.urls import reverse

from inventory import forms
from inventory.views.product_editor import SetupVariations


@pytest.fixture
def product_range(product_range_factory):
    return product_range_factory.create()


@pytest.fixture
def initial_variation(product_range, initial_variation_factory):
    return initial_variation_factory.create(product_range=product_range)


@pytest.fixture
def url(product_range):
    return reverse("inventory:setup_variations", kwargs={"range_pk": product_range.pk})


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.fixture
def mock_form(product_range):
    with mock.patch(
        "inventory.views.product_editor.SetupVariations.get_form_class",
    ) as mock_get_form_class:
        mock_form = mock.MagicMock()
        mock_form.is_valid = mock.Mock(return_value=True)
        mock_form.save = mock.Mock()
        mock_form.fields.items.return_value = (
            ("key1", mock.Mock(label="value1")),
            ("key2", mock.Mock(label="value2")),
        )
        mock_form.cleaned_data = {"variations": "[]"}
        mock_get_form_class.return_value.return_value = mock_form
        yield mock_form


@pytest.fixture
def post_response(post_data, group_logged_in_client, url):
    return group_logged_in_client.post(url, post_data)


@pytest.mark.django_db
def test_uses_template(get_response):
    assert "inventory/product_editor/setup_variations.html" in [
        t.name for t in get_response.templates
    ]


@pytest.mark.django_db
def test_form_in_context(get_response):
    form = get_response.context["form"]
    assert isinstance(form, forms.SetupVariationsForm)


@pytest.mark.django_db
def test_get_options(mock_form):
    options = SetupVariations().get_options(mock_form)
    assert options == '{"key1": "value1", "key2": "value2"}'


@pytest.mark.django_db
def test_options_in_context(group_logged_in_client, url):
    with mock.patch(
        "inventory.views.product_editor.SetupVariations.get_options"
    ) as mock_get_options:
        context = group_logged_in_client.get(url).context
        assert context["options"] == mock_get_options.return_value


@pytest.mark.django_db
def test_success_redirect(
    mock_form, initial_variation, group_logged_in_client, url, product_range
):
    response = group_logged_in_client.post(url, {})
    assert response.status_code == 302
    assert response["location"] == reverse(
        "inventory:edit_all_variations", kwargs={"range_pk": product_range.pk}
    )


@pytest.mark.django_db
def test_calls_create_variations(mock_form, url, group_logged_in_client):
    mock_form.cleaned_data["variations"] = json.dumps(
        [
            {"options": ["One", "Two", "Three"], "included": True},
            {"options": ["Three", "Four", "Five"], "included": False},
            {"options": ["Six", "Seven", "Eight"], "included": True},
        ]
    )
    with mock.patch(
        "inventory.views.product_editor.models.InitialVariation.objects.get"
    ) as mock_get_initial_variation:
        group_logged_in_client.post(url)
        mock_get_initial_variation.return_value.create_variations.assert_called_once_with(
            [["One", "Two", "Three"], ["Six", "Seven", "Eight"]]
        )


@pytest.mark.django_db
def test_deletes_initial_variation(mock_form, url, group_logged_in_client):
    with mock.patch(
        "inventory.views.product_editor.models.InitialVariation.objects.get"
    ) as mock_get_initial_variation:
        group_logged_in_client.post(url)
        mock_get_initial_variation.return_value.delete.assert_called_once_with()
