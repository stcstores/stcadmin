import pytest
from django.shortcuts import reverse
from django.template.loader import render_to_string


@pytest.fixture
def section_navigation_content():
    return render_to_string("orders/section_navigation.html")


@pytest.mark.parametrize(
    "name,link",
    [
        ("Orders", "orders:index"),
        ("Breakages", "orders:breakages"),
        ("Charts", "orders:charts"),
        ("Undispatched Orders", "orders:undispatched_orders"),
        ("Order List", "orders:order_list"),
    ],
)
def test_orders_section_navigation(name, link, section_navigation_content):
    link_text = f'<a href="{reverse(link)}">{name}</a>'
    assert link_text in section_navigation_content
