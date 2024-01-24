import pytest

from channels.forms import ShopifyTagsForm


@pytest.fixture
def shopify_listing(shopify_listing_factory):
    return shopify_listing_factory.create()


@pytest.fixture
def tags(shopify_tag_factory):
    return shopify_tag_factory.create_batch(3)


@pytest.fixture
def form_data(tags):
    return {"tags": [tag for tag in tags]}


@pytest.mark.django_db
def test_form_submission(tags, shopify_listing, form_data):
    form = ShopifyTagsForm(form_data, instance=shopify_listing)
    assert form.is_valid() is True
    form.save()
    for tag in tags:
        assert form.instance.tags.all().contains(tag)


@pytest.mark.django_db
def test_remove_tags(tags, shopify_listing):
    shopify_listing.tags.set(tags)
    form = ShopifyTagsForm({"tags": []}, instance=shopify_listing)
    assert form.is_valid() is True
    form.save()
    assert shopify_listing.tags.count() == 0
