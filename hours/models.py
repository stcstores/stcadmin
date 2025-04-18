"""Models for the Hours app."""

import calendar
import csv
import datetime as dt
from io import StringIO

from django.conf import settings
from django.core.mail import EmailMessage
from django.db import models, transaction
from django.utils import timezone
from solo.models import SingletonModel

from home.models import Staff


class HoursSettings(SingletonModel):
    """Model for storing settings for the hours app."""

    send_report_to = models.EmailField(null=True)

    class Meta:
        """Meta class for HoursSettings."""

        verbose_name = "Hours Settings"


class ClockTime(models.Model):
    """Model for storing clock ins and outs."""

    IN = "In"
    OUT = "Out"

    user = models.ForeignKey(
        Staff, on_delete=models.PROTECT, related_name="clock_hours"
    )
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        """Meta class for the ClockTime model."""

        verbose_name = "Clock Time"
        verbose_name_plural = "Clock Times"
        ordering = ("timestamp",)
        unique_together = [["user", "timestamp"]]
        get_latest_by = "timestamp"

    class ClockTimeManager(models.Manager):
        """Manager for the ClockTime model."""

        def clock(self, user):
            """Create a clock time."""
            now = timezone.now().replace(microsecond=0)
            now_naive = timezone.make_naive(now)
            lower_bound = timezone.make_aware(
                dt.datetime(
                    year=now_naive.year,
                    month=now_naive.month,
                    day=now_naive.day,
                    hour=now_naive.hour,
                    minute=now_naive.minute,
                )
            )
            upper_bound = lower_bound + dt.timedelta(minutes=1)
            if self.filter(
                user=user, timestamp__gte=lower_bound, timestamp__lte=upper_bound
            ).exists():
                raise self.model.ClockedTooSoonError()
            obj = self.create(user=user, timestamp=now)
            return obj

    class ClockedTooSoonError(ValueError):
        """Error raised when two clocks are recorded for the same user in the same minute."""

        def __init__(self, *args, **kwargs):
            """Raise error."""
            super().__init__(self, "Clocked too soon.")

    objects = ClockTimeManager()

    def __str__(self):
        return f"Clock {self.user} at {self.timestamp}"

    def direction(self):
        """Return ClockTime.IN or ClockTime.OUT."""
        day_start = timezone.make_aware(
            dt.datetime.combine(self.timestamp.date(), dt.datetime.min.time())
        )
        earlier_times = ClockTime.objects.filter(
            user=self.user,
            timestamp__range=(day_start, self.timestamp),
        ).exclude(id=self.id)
        if earlier_times.count() % 2 == 0:
            return self.IN
        return self.OUT


class HoursExportReport:
    """Generate reports for hours exports."""

    def __init__(self, month, year):
        """Generate an hours report."""
        self.month = month
        self.year = year
        self.month_length = calendar.monthrange(self.year, self.month)[1]
        self.header = [f"{calendar.month_name[month]} {year}"]
        self.header.extend(list(range(1, self.month_length + 1)))

    def generate_report_text(self):
        """Return io.StringIO containing the report as a .csv."""
        rows = self._get_report_data()
        output = StringIO()
        writer = csv.writer(output)
        writer.writerows(rows)
        return output

    def _get_report_data(self):
        staff = Staff.objects.filter(can_clock_in=True)
        rows = []
        for staff_member in staff:
            rows.append(self.header)
            rows.append(self._get_row(staff_member))
        return rows

    def _get_row(self, staff_member):
        row = [staff_member.full_name()]
        for day_number in range(1, self.month_length + 1):
            date = dt.date(day=day_number, month=self.month, year=self.year)
            row.append(self._get_day(staff_member, date))
        return row

    def _get_day(self, staff_member, date):
        clocks = ClockTime.objects.filter(user=staff_member, timestamp__date=date)
        return "\n".join([_.timestamp.strftime("%H:%M") for _ in clocks])


class HoursExport(models.Model):
    """Model for hours exports."""

    export_date = models.DateField(default=timezone.now, unique=True)
    created_at = models.DateTimeField(default=timezone.now)
    report_sent = models.BooleanField(default=False)

    class Meta:
        """Meta class for HoursExport."""

        verbose_name = "Hours Export"
        verbose_name_plural = "Hours Exports"
        ordering = ("-export_date",)

    class HoursExportManager(models.Manager):
        """Manager for the HoursExport model."""

        @transaction.atomic
        def new_export(self):
            """Create a new hours export."""
            export = self.create(export_date=timezone.now() - dt.timedelta(days=1))
            return export

    objects = HoursExportManager()

    def __str__(self):
        return f"Hours Report {self.export_date.strftime('%b %Y')}"

    def generate_report(self):
        """Return a .csv report as io.StringIO."""
        return HoursExportReport(
            self.export_date.month, self.export_date.year
        ).generate_report_text()

    def get_report_filename(self):
        """Return a filename for .csv reports based on this expot."""
        return f"staff_hours_{self.export_date.strftime('%b_%Y')}.csv"

    def send_report_email(self):
        """Send montly staff hours report email."""
        if self.report_sent is True:
            raise Exception(f"{self} Already Sent.")
        message_body = "Please find this months staff hours report attached."
        message = EmailMessage(
            subject=f"Staff Hours Report {self.export_date.strftime('%b %Y')}",
            body=message_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[HoursSettings.get_solo().send_report_to],
        )
        message.attach(
            self.get_report_filename(),
            self.generate_report().getvalue(),
            "text/csv",
        )
        message.send()
        self.report_sent = True
        self.save()
