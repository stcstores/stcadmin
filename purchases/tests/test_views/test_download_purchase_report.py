import datetime as dt

import pytest
from django.urls import reverse


@pytest.fixture
def date():
    return dt.date(day=1, month=2, year=2023)


@pytest.fixture
def purchase_export(date, purchase_export_factory):
    return purchase_export_factory.create(export_date=date)


@pytest.fixture
def url(purchase_export):
    return reverse(
        "purchases:download_purchase_report", kwargs={"pk": purchase_export.pk}
    )


@pytest.fixture
def get_response(group_logged_in_client, url):
    return group_logged_in_client.get(url)


@pytest.mark.django_db
def test_content_disposition(get_response):
    content_disposition = get_response.headers["Content-Disposition"]
    assert content_disposition == "attachment;filename=purchase_report_Feb_2023.csv"


@pytest.mark.django_db
def test_response_text(purchase_export, get_response):
    expected_value = purchase_export.generate_report().getvalue().encode("utf-8")
    assert get_response.getvalue() == expected_value
