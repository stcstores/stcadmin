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
            now = timezone.now()
            try:
                latest = self.filter(user=user).latest().timestamp
            except self.model.DoesNotExist:
                pass
            else:
                if all(
                    (
                        latest.year == now.year,
                        latest.month == now.month,
                        latest.day == now.day,
                        latest.hour == now.hour,
                        latest.minute == now.minute,
                    ),
                ):
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
        earlier_times = ClockTime.objects.filter(
            user=self.user, timestamp__range=(self.timestamp.date().min, self.timestamp)
        ).exclude(id=self.id)
        if earlier_times.count() % 2 == 0:
            return self.IN
        return self.OUT


class HoursExportReport:
    """Generate reports for hours exports."""

    @classmethod
    def generate_report_text(cls, month, year):
        """Return io.StringIO containing the report as a .csv."""
        rows = cls._get_report_data(month, year)
        output = StringIO()
        writer = csv.writer(output)
        writer.writerows(rows)
        return output

    @staticmethod
    def _get_report_data(month, year):
        number_of_days = calendar.monthrange(year, month)[1]
        header = [f"{calendar.month_name[month]} {year}"]
        header.extend(list(range(1, number_of_days + 1)))
        staff = Staff.objects.filter(can_clock_in=True)
        rows = []
        for staff_member in staff:
            rows.append(header)
            row = [staff_member.full_name()]
            for day_number in range(1, number_of_days + 1):
                date = dt.date(day=day_number, month=month, year=year)
                clocks = ClockTime.objects.filter(
                    user=staff_member, timestamp__date=date
                )
                row.append("\n".join([_.timestamp.strftime("%H:%M") for _ in clocks]))
            rows.append(row)
        return rows


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
        return HoursExportReport.generate_report_text(
            self.export_date.month, self.export_date.year
        )

    def get_report_filename(self):
        """Return a filename for .csv reports based on this expot."""
        return f"hours_{self.export_date.strftime('%b_%Y')}.csv"

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
