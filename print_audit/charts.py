"""Charts for print audit app."""

import datetime

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
    WEEKS_TO_DISPLAY = 52

    def __init__(self, *args, **kwargs):
        """Get weeks in range."""
        years = [
            d.year
            for d in models.CloudCommerceOrder.objects.all().datetimes(
                "date_created", "year"
            )
        ]

        class Week:
            def __init__(self, year, number):
                self.year = year
                self.number = number
                self.monday = datetime.datetime.strptime(
                    f"{self.year}-W{self.number}-1", "%Y-W%W-%w"
                )
                self.name = self.monday.strftime("%d-%b-%Y")
                self.value = models.CloudCommerceOrder.objects.filter(
                    date_created__year=year, date_created__week=number
                ).count()

        weeks_numbers = list(range(1, self.WEEKS_TO_DISPLAY + 1))
        self.weeks = []
        self.now = datetime.datetime.now()
        self.first_order_date = (
            models.CloudCommerceOrder.objects.order_by("date_created")
            .all()[0]
            .date_created
        )
        for year in years:
            for week in weeks_numbers:
                if self.week_required(year, week):
                    self.weeks.append(Week(year, week))
        super().__init__(*args, **kwargs)

    def week_required(self, year, week):
        """Return True if week is in required range."""
        if year == self.now.year and week > self.get_week(self.now) - 1:
            return False
        first_week = self.get_week(self.first_order_date)
        first_year = self.first_order_date.year
        if year == first_year and week < first_week + 1:
            return False
        return True

    def get_week(self, date):
        """Return week number for date."""
        return date.isocalendar()[1]

    def get_labels(self):
        """Return axis labels for weeks."""
        return [w.name for w in self.weeks]

    def get_datasets(self, **kwargs):
        """Return datasets for chart."""
        data = [w.value for w in self.weeks]
        return [DataSet(data=data, color=(85, 79, 255))]
