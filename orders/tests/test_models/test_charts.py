from datetime import date, datetime, timedelta
from unittest.mock import patch

from django.utils.timezone import make_aware
from isoweek import Week

from orders import models
from stcadmin.tests.stcadmin_test import STCAdminTest


class TestOrdersByDayChart(STCAdminTest):
    fixtures = (
        "home/cloud_commerce_user",
        "shipping/currency",
        "shipping/region",
        "shipping/country",
        "shipping/provider",
        "shipping/courier_type",
        "shipping/courier",
        "shipping/courier_service",
        "shipping/shipping_rule",
        "orders/channel",
        "orders/order",
        "orders/product_sale",
        "orders/packing_record",
    )

    @patch("orders.models.charts.timezone.now")
    def test_labels(self, mock_now):
        mock_date = make_aware(datetime(2019, 12, 4))
        mock_now.return_value = mock_date
        chart = models.charts.OrdersByDay()
        labels = chart.get_labels()
        self.assertIsInstance(labels, list)
        self.assertEqual(chart.DAYS_TO_DISPLAY, len(labels))
        self.assertEqual(mock_date.strftime("%a %d %b %Y"), labels[-1])
        self.assertEqual(
            (mock_date - timedelta(days=chart.DAYS_TO_DISPLAY - 1)).strftime(
                "%a %d %b %Y"
            ),
            labels[0],
        )

    @patch("orders.models.charts.timezone.now")
    def test_count_orders(self, mock_now):
        mock_date = make_aware(datetime(2019, 12, 4))
        mock_now.return_value = mock_date
        chart = models.charts.OrdersByDay()
        orders = chart.count_orders()
        self.assertIsInstance(orders, dict)
        self.assertEqual(chart.DAYS_TO_DISPLAY, len(orders))
        self.assertEqual(mock_date.date(), list(orders.keys())[-1])
        self.assertEqual(
            (mock_date - timedelta(days=chart.DAYS_TO_DISPLAY - 1)).date(),
            list(orders.keys())[0],
        )
        for key, value in orders.items():
            self.assertIsInstance(key, date)
        self.assertEqual(8, orders[date(2019, 12, 3)])

    @patch("orders.models.charts.timezone.now")
    def test_datasets(self, mock_now):
        mock_date = make_aware(datetime(2019, 12, 4))
        mock_now.return_value = mock_date
        chart = models.charts.OrdersByDay()
        datasets = chart.get_datasets()
        self.assertEqual(1, len(datasets))
        dataset = datasets[0]
        expected_data = [0 for i in range(chart.DAYS_TO_DISPLAY)]
        expected_data[28] = 1
        expected_data[58] = 8
        expected_data[59] = 2
        self.assertEqual(expected_data, dataset["data"])


class TestOrdersByWeekChart(STCAdminTest):
    fixtures = (
        "home/cloud_commerce_user",
        "shipping/currency",
        "shipping/region",
        "shipping/country",
        "shipping/provider",
        "shipping/courier_type",
        "shipping/courier",
        "shipping/courier_service",
        "shipping/shipping_rule",
        "orders/channel",
        "orders/order",
        "orders/product_sale",
        "orders/packing_record",
    )

    @patch("orders.models.charts.Week.thisweek")
    def test_labels(self, mock_now):
        mock_date = Week(2019, 50)
        mock_now.return_value = mock_date
        chart = models.charts.OrdersByWeek(number_of_weeks=5)
        labels = chart.get_labels()
        self.assertEqual(
            [
                Week(2019, 45).monday().strftime("%d-%b-%Y %V"),
                Week(2019, 46).monday().strftime("%d-%b-%Y %V"),
                Week(2019, 47).monday().strftime("%d-%b-%Y %V"),
                Week(2019, 48).monday().strftime("%d-%b-%Y %V"),
                Week(2019, 49).monday().strftime("%d-%b-%Y %V"),
            ],
            labels,
        )

    @patch("orders.models.charts.Week.thisweek")
    def test_order_counts(self, mock_now):
        mock_date = Week(2019, 50)
        mock_now.return_value = mock_date
        chart = models.charts.OrdersByWeek(number_of_weeks=5)
        order_counts = chart.get_order_counts(*chart.dates())
        self.assertDictEqual(
            {
                Week(2019, 45): 0,
                Week(2019, 46): 0,
                Week(2019, 47): 0,
                Week(2019, 48): 0,
                Week(2019, 49): 10,
            },
            order_counts,
        )

    @patch("orders.models.charts.Week.thisweek")
    def test_dataset(self, mock_now):
        mock_date = Week(2019, 50)
        mock_now.return_value = mock_date
        chart = models.charts.OrdersByWeek(number_of_weeks=5)
        datasets = chart.get_datasets()
        self.assertEqual(1, len(datasets))
        dataset = datasets[0]
        self.assertEqual([0, 0, 0, 0, 10], dataset["data"])
