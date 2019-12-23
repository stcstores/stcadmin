"""Order charts."""

from datetime import datetime, timedelta

from django.utils import timezone
from isoweek import Week
from jchart import Chart
from jchart.config import Axes, DataSet

from orders import models


class OrdersByDay(Chart):
    """Chart number of orders by day dispatched."""

    chart_type = "horizontalBar"
    scales = {"yAxes": [Axes(ticks={"beginAtZero": True})]}
    legend = {"display": False}
    title = {"display": True, "text": "Orders by Day"}
    DAYS_TO_DISPLAY = 60

    def __init__(self, *args, **kwargs):
        """Count orders."""
        self.order_counts = self.count_orders()
        super().__init__(*args, **kwargs)

    def count_orders(self):
        """Get orders for dates to be charted."""
        now = timezone.now()
        today = timezone.make_aware(datetime(now.year, now.month, now.day))
        date_from = today - timedelta(days=self.DAYS_TO_DISPLAY - 1)
        order_dates = models.Order.objects.filter(
            dispatched_at__isnull=False,
            dispatched_at__gte=date_from,
            dispatched_at__lte=today + timedelta(days=1),
        ).values_list("dispatched_at__date", flat=True)
        dates = [
            date_from.date() + timedelta(days=i) for i in range(self.DAYS_TO_DISPLAY)
        ]
        order_counts = {date: 0 for date in sorted(list(set(dates)))}
        for date in order_dates:
            order_counts[date] += 1
        return order_counts

    def get_labels(self):
        """Return axis labels for dates."""
        return [day.strftime("%a %d %b %Y") for day in self.order_counts.keys()]

    def get_datasets(self, **kwargs):
        """Return datasets for chart."""
        red = "#ff554f"
        green = "#4fff55"
        blue = "#554fff"
        colours = []
        data = []
        day_colours = [red, blue, blue, blue, blue, green, green]
        for day, count in self.order_counts.items():
            data.append(count)
            colours.append(day_colours[day.weekday()])
        return [DataSet(data=data, backgroundColor=colours)]


class OrdersByWeek(Chart):
    """Chart number of orders dispatched by week."""

    chart_type = "line"
    scales = {"yAxes": [Axes(ticks={"beginAtZero": True})]}
    legend = {"display": False}
    title = {"display": True, "text": "Orders by Week"}

    def __init__(self, *args, **kwargs):
        """Get weeks in range."""
        self.number_of_weeks = kwargs.pop("number_of_weeks")
        date_from, date_to = self.dates()
        self.order_counts = self.get_order_counts(date_from, date_to)
        super().__init__(*args, **kwargs)

    def dates(self):
        """Return the start and end dates for the order count query."""
        end_week = Week.thisweek()
        start_week = end_week - self.number_of_weeks
        date_to = timezone.make_aware(
            datetime.combine(end_week.monday(), datetime.min.time())
        )
        date_from = timezone.make_aware(
            datetime.combine(start_week.monday(), datetime.min.time())
        )
        return date_from, date_to

    def get_order_counts(self, date_from, date_to):
        """Return the number of orders for each week."""
        order_dates = self.order_dates(date_from, date_to)
        start_year, start_week, start_day = date_from.isocalendar()
        start_week = Week(start_year, start_week)
        order_counts = {start_week + i: 0 for i in range(self.number_of_weeks)}
        for date in order_dates:
            year, week, day = date.isocalendar()
            order_counts[Week(year, week)] += 1
        return order_counts

    def order_dates(self, date_from, date_to):
        """Return a list of order dispatch dates."""
        return models.Order.objects.filter(
            dispatched_at__isnull=False,
            dispatched_at__gte=date_from,
            dispatched_at__lt=date_to,
        ).values_list("dispatched_at", flat=True)

    def get_labels(self):
        """Return axis labels for weeks."""
        return [week.monday().strftime("%d-%b-%Y %V") for week in self.order_counts]

    def get_datasets(self, **kwargs):
        """Return datasets for chart."""
        return [DataSet(data=list(self.order_counts.values()), color=(85, 79, 255))]
