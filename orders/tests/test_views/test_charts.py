import pytest
from pytest_django.asserts import assertTemplateUsed

from orders import models


@pytest.fixture
def url():
    return "/orders/charts/"


@pytest.fixture
def valid_get_response(valid_get_request, url):
    return valid_get_request(url)


def test_logged_in_get(url, logged_in_client):
    response = logged_in_client.get(url)
    assert response.status_code == 403


def test_logged_out_get(client, url):
    response = client.get(url)
    assert response.status_code == 302


def test_logged_in_group_get(group_logged_in_client, url):
    response = group_logged_in_client.get(url)
    assert response.status_code == 200


def test_logged_in_post(url, logged_in_client):
    response = logged_in_client.post(url)
    assert response.status_code == 403


def test_logged_out_post(client, url):
    response = client.post(url)
    assert response.status_code == 302


@pytest.mark.django_db
def test_logged_in_group_post(group_logged_in_client, url):
    response = group_logged_in_client.post(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_uses_template(valid_get_response):
    assert assertTemplateUsed(valid_get_response, "orders/charts.html") is not False


@pytest.mark.django_db
def test_orders_by_week_chart_is_in_context(valid_get_response):
    chart = valid_get_response.context["orders_by_week_chart"]
    assert isinstance(chart, models.charts.OrdersByWeek)


@pytest.mark.django_db
def test_orders_by_day_chart_is_in_context(valid_get_response):
    chart = valid_get_response.context["orders_by_day_chart"]
    assert isinstance(chart, models.charts.OrdersByDay)


@pytest.mark.django_db
def test_number_of_weeks(group_logged_in_client, url):
    response = group_logged_in_client.post(url, {"number_of_weeks": 5})
    chart = response.context["orders_by_week_chart"]
    assert len(chart.get_datasets()[0]["data"]) == 5
