import pytest

from channels.forms import ShopifyTagForm


@pytest.fixture
def shopify_tag(shopify_tag_factory):
    return shopify_tag_factory.create()


@pytest.fixture
def form_data():
    return {"name": "Tag Name"}


@pytest.mark.django_db
def test_object_creation(form_data):
    form = ShopifyTagForm(form_data)
    assert form.is_valid() is True
    form.save()
    assert form.instance.pk
    assert form.instance.name == form_data["name"]


@pytest.mark.django_db
def test_object_update(shopify_tag, form_data):
    form = ShopifyTagForm(form_data, instance=shopify_tag)
    assert form.is_valid() is True
    form.save()
    shopify_tag.refresh_from_db()
    assert form.instance.name == form_data["name"]
