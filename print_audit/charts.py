"""Charts for print audit app."""

import datetime

from isoweek import Week
from jchart import Chart
from jchart.config import Axes, DataSet

from print_audit import models


class OrdersByDay(Chart):
    """Chart number of orders by day dispatched."""

    chart_type = "horizontalBar"
    scales = {"yAxes": [Axes(ticks={"beginAtZero": True})]}
    legend = {"display": False}
    title = {"display": True, "text": "Orders by Day"}
    DAYS_TO_DISPLAY = 60

    def __init__(self, *args, **kwargs):
        """Get orders for dates to be charted."""
        self.today = datetime.datetime.today()
        day = self.today - datetime.timedelta(days=self.DAYS_TO_DISPLAY)
        self.orders = {}
        while day <= self.today:
            self.orders[day] = models.CloudCommerceOrder.objects.filter(
                date_created__date=day
            ).count()
            day = day + datetime.timedelta(days=1)
        super().__init__(*args, **kwargs)

    def get_labels(self):
        """Return axis labels for dates."""
        return [day.strftime("%a %d %b %Y") for day, count in self.orders.items()]

    def get_datasets(self, **kwargs):
        """Return datasets for chart."""
        red = "#ff554f"
        green = "#4fff55"
        blue = "#554fff"
        colours = []
        data = []
        day_colours = [red, blue, blue, blue, blue, green, green]
        for day, count in self.orders.items():
            data.append(count)
            colours.append(day_colours[day.weekday()])
        return [{"data": data, "backgroundColor": colours}]


class OrdersByWeek(Chart):
    """Chart number of orders dispatched by week."""

    chart_type = "line"
    scales = {"yAxes": [Axes(ticks={"beginAtZero": True})]}
    legend = {"display": False}
    title = {"display": True, "text": "Orders by Week"}

    def __init__(self, number_of_weeks):
        """Get weeks in range."""
        self.number_of_weeks = number_of_weeks
        self.now = datetime.datetime.now()
        self.weeks = self.get_weeks()
        self.order_counts = [self.order_count_for_week(week) for week in self.weeks]
        self.labels = [week.monday().strftime("%d-%b-%Y") for week in self.weeks]
        super().__init__()

    def get_weeks(self):
        """Return a list of weeks to display as tuples of year and week number."""
        weeks = []
        last_week = Week.thisweek() - 1
        week = last_week - self.number_of_weeks
        while week <= last_week:
            weeks.append(week)
            week += 1
        return weeks

    @staticmethod
    def order_count_for_week(week):
        """Return the number of orders processed for a week."""
        return models.CloudCommerceOrder.objects.filter(
            date_created__year=week.year, date_created__week=week.week
        ).count()

    def get_labels(self):
        """Return axis labels for weeks."""
        return self.labels

    def get_datasets(self, **kwargs):
        """Return datasets for chart."""
        return [DataSet(data=self.order_counts, color=(85, 79, 255))]
