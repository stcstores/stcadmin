import pytest
from django.contrib import messages
from django.urls import reverse

from inventory import forms


@pytest.fixture
def product_range(product_range_factory):
    return product_range_factory.create()


@pytest.fixture
def url(product_range):
    return reverse("inventory:descriptions", kwargs={"pk": product_range.pk})


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.fixture
def managed_by_user(user_factory):
    return user_factory.create()


@pytest.fixture
def post_data(managed_by_user):
    return {"managed_by": managed_by_user.pk}


@pytest.fixture
def post_response(post_data, group_logged_in_client, url):
    return group_logged_in_client.post(url, post_data)


@pytest.mark.django_db
def test_description_view_context_contains_form(get_response):
    form = get_response.context["form"]
    assert isinstance(form, forms.EditRangeForm)


@pytest.mark.django_db
def test_description_view_context_contains_product_range(get_response, product_range):
    assert get_response.context["product_range"] == product_range


@pytest.mark.django_db
def test_uses_template(get_response):
    assert "inventory/product_range/descriptions.html" in [
        t.name for t in get_response.templates
    ]


@pytest.mark.django_db
def test_success_url(product_range, post_response):
    assert post_response.status_code == 302
    assert post_response["location"] == reverse(
        "inventory:descriptions", kwargs={"pk": product_range.pk}
    )


@pytest.mark.django_db
def test_success_adds_message(post_data, group_logged_in_client, url):
    post_response = group_logged_in_client.post(url, post_data, follow=True)
    message = list(post_response.context["messages"])[0]
    assert message.message == "Description Updated"
    assert message.level == messages.SUCCESS
