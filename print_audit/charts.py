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

    def __init__(self, number_of_weeks):
        """Get weeks in range."""
        self.number_of_weeks = number_of_weeks
        self.now = datetime.datetime.now()
        self.weeks = self.get_weeks()
        self.order_counts = [self.order_count_for_week(*_) for _ in self.weeks]
        self.labels = [self.label_for_week(*_) for _ in self.weeks]
        super().__init__()

    def get_weeks(self):
        """Return a list of weeks to display as tuples of year and week number."""
        weeks = []
        initial_date = self.now - datetime.timedelta(weeks=self.number_of_weeks)
        start_year = self.calendar_year(initial_date)
        first_week = self.week_number(initial_date)
        for year in range(start_year, self.calendar_year(self.now) + 1):
            if year != start_year:
                first_week = 1
            if year == self.calendar_year(self.now):
                last_week = self.week_number(self.now)
            else:
                last_week = self.last_week(year)
            for week_number in range(first_week, last_week + 1):
                if week_number == self.week_number(self.now):
                    continue
                weeks.append((year, week_number))
        return weeks

    def last_week(self, year):
        """Return the last week number for a year."""
        return self.week_number(datetime.datetime(year, 12, 28))

    def week_number(self, date):
        """Return week number for date."""
        return date.isocalendar()[1]

    @staticmethod
    def order_count_for_week(year, week_number):
        """Return the number of orders processed for a week."""
        return models.CloudCommerceOrder.objects.filter(
            date_created__year=year, date_created__week=week_number
        ).count()

    @staticmethod
    def label_for_week(year, week_number):
        """Return the start date for a week as a string."""
        monday = datetime.datetime.strptime(f"{year}-W{week_number}-1", "%Y-W%W-%w")
        return monday.strftime("%d-%b-%Y")

    def calendar_year(self, date):
        """Return the calendar year for a given date.

        Use this instead of date.year to prevent errors on weeks including the first day
        of the year.
        """
        return date.isocalendar()[0]

    def get_labels(self):
        """Return axis labels for weeks."""
        return self.labels

    def get_datasets(self, **kwargs):
        """Return datasets for chart."""
        return [DataSet(data=self.order_counts, color=(85, 79, 255))]
