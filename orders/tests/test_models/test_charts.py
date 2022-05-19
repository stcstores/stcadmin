from datetime import date, datetime, timedelta
from unittest.mock import patch

import pytest
from django.utils.timezone import make_aware
from isoweek import Week

from orders import models


@pytest.fixture
def mock_now():
    with patch("orders.models.charts.timezone.now") as mock_now:
        yield mock_now


@pytest.fixture
def mock_this_week():
    with patch("orders.models.charts.Week.thisweek") as mock_this_week:
        yield mock_this_week


@pytest.fixture
def orders(order_factory):
    order_factory.create(dispatched_at=make_aware(datetime(2019, 11, 3)))
    for _ in range(8):
        order_factory.create(dispatched_at=make_aware(datetime(2019, 12, 3)))
    for _ in range(2):
        order_factory.create(dispatched_at=make_aware(datetime(2019, 12, 4)))


@pytest.mark.django_db
def test_orders_by_day_chart_labels(orders, mock_now):
    mock_date = make_aware(datetime(2019, 12, 4))
    mock_now.return_value = mock_date
    chart = models.charts.OrdersByDay()
    labels = chart.get_labels()
    assert isinstance(labels, list)
    assert chart.DAYS_TO_DISPLAY == len(labels)
    assert labels[-1] == mock_date.strftime("%a %d %b %Y")
    assert labels[0] == (
        mock_date - timedelta(days=chart.DAYS_TO_DISPLAY - 1)
    ).strftime("%a %d %b %Y")


@pytest.mark.django_db
def test_orders_by_day_chart_count_orders(orders, mock_now):
    mock_date = make_aware(datetime(2019, 12, 4))
    mock_now.return_value = mock_date
    chart = models.charts.OrdersByDay()
    orders = chart.count_orders()
    assert isinstance(orders, dict)
    assert chart.DAYS_TO_DISPLAY == len(orders)
    assert mock_date.date() == list(orders.keys())[-1]
    assert (
        list(orders.keys())[0]
        == (mock_date - timedelta(days=chart.DAYS_TO_DISPLAY - 1)).date()
    )
    for key, value in orders.items():
        assert isinstance(key, date)
    assert orders[date(2019, 12, 3)] == 8


@pytest.mark.django_db
def test_orders_by_day_chart_datasets(orders, mock_now):
    mock_date = make_aware(datetime(2019, 12, 4))
    mock_now.return_value = mock_date
    chart = models.charts.OrdersByDay()
    datasets = chart.get_datasets()
    assert len(datasets) == 1
    dataset = datasets[0]
    expected_data = [0 for i in range(chart.DAYS_TO_DISPLAY)]
    expected_data[28] = 1
    expected_data[58] = 8
    expected_data[59] = 2
    for i, v in enumerate(dataset["data"]):
        if v != 0:
            print(i, v)
    assert dataset["data"] == expected_data


@pytest.mark.django_db
def test_orders_by_week_labels(orders, mock_this_week):
    mock_date = Week(2019, 50)
    mock_this_week.return_value = mock_date
    chart = models.charts.OrdersByWeek(number_of_weeks=5)
    labels = chart.get_labels()
    assert labels == [
        Week(2019, 45).monday().strftime("%d-%b-%Y %V"),
        Week(2019, 46).monday().strftime("%d-%b-%Y %V"),
        Week(2019, 47).monday().strftime("%d-%b-%Y %V"),
        Week(2019, 48).monday().strftime("%d-%b-%Y %V"),
        Week(2019, 49).monday().strftime("%d-%b-%Y %V"),
    ]


@pytest.mark.django_db
def test_orders_by_week_order_counts(orders, mock_this_week):
    mock_date = Week(2019, 50)
    mock_this_week.return_value = mock_date
    chart = models.charts.OrdersByWeek(number_of_weeks=5)
    order_counts = chart.get_order_counts(*chart.dates())
    assert order_counts == {
        Week(2019, 45): 0,
        Week(2019, 46): 0,
        Week(2019, 47): 0,
        Week(2019, 48): 0,
        Week(2019, 49): 10,
    }


@pytest.mark.django_db
def test_orders_by_week_dataset(orders, mock_this_week):
    mock_date = Week(2019, 50)
    mock_this_week.return_value = mock_date
    chart = models.charts.OrdersByWeek(number_of_weeks=5)
    datasets = chart.get_datasets()
    assert len(datasets) == 1
    dataset = datasets[0]
    assert dataset["data"] == [0, 0, 0, 0, 10]
