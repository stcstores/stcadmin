import pytest
from django.shortcuts import reverse
from django.template.loader import render_to_string
from requests_html import HTML


@pytest.fixture
def section_navigation_content():
    return render_to_string("orders/section_navigation.html")


@pytest.fixture
def page_html(section_navigation_content):
    return HTML(html=section_navigation_content)


@pytest.mark.parametrize(
    "name,reverse_path",
    [
        ("Orders", "orders:index"),
        ("Charts", "orders:charts"),
        ("Undispatched Orders", "orders:undispatched_orders"),
        ("Order List", "orders:order_list"),
        ("Refunds", "orders:refund_list"),
    ],
)
def test_orders_section_navigation(name, reverse_path, page_html):
    assert page_html.find(f'a[href="{reverse(reverse_path)}"]', containing=name)
