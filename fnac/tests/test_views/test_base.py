import pytest
from django.shortcuts import reverse

PAGES = [
    reverse("fnac:index"),
    reverse("fnac:invalid_in_inventory"),
    reverse("fnac:missing_information"),
    reverse("fnac:translations"),
    reverse("fnac:shipping_comment"),
]


@pytest.mark.parametrize("page", PAGES)
def test_page_navigation(page, group_logged_in_client):
    content = group_logged_in_client.get(page).content.decode("utf8")
    for link in PAGES:
        assert link in content
