import pytest
from django.shortcuts import reverse

PAGES = [
    reverse("fnac:index"),
    reverse("fnac:update_offers"),
    reverse("fnac:create_products"),
]


@pytest.mark.parametrize("page", PAGES)
def test_page_navigation(page, group_logged_in_client):
    content = group_logged_in_client.get(page).content.decode("utf8")
    for link in PAGES:
        assert link in content
