"""Views for reports."""

from django.http import HttpResponse, HttpResponseNotFound
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView, View

from home.views import UserInGroupMixin
from reports import forms, models


class ReportsUserMixin(UserInGroupMixin):
    """View mixin to ensure user is in the fba group."""

    groups = ["fba"]


class Index(ReportsUserMixin, TemplateView):
    """Reports index view."""

    template_name = "reports/index.html"


class BaseReportPage(ReportsUserMixin, TemplateView):
    """Base view for report pages."""

    report_name = ""
    form_class = None
    create_report_url = None
    status_url = None
    report_list_url = None

    def get_form(self):
        """Return a form instance if form_class is not None, else return None."""
        if self.form_class is None:
            return None
        else:
            return self.form_class()

    def get_context_data(self, *args, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(*args, **kwargs)
        context["report_name"] = self.report_name
        context["form"] = self.get_form()
        context["create_report_url"] = self.create_report_url
        context["report_list_url"] = self.report_list_url
        context["status_url"] = self.status_url
        return context


class BaseReportList(ReportsUserMixin, TemplateView):
    """Base view for report lists."""

    model = None
    max_reports = 50

    def get_context_data(self, *args, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(*args, **kwargs)
        qs = self.model.objects.filter(status=self.model.COMPLETE)
        context["reports"] = qs[: self.max_reports]
        return context


class BaseCreateReport(ReportsUserMixin, View):
    """Base view for requesting new reports."""

    form_class = None
    model = None

    def get_create_download_kwargs(self, form_data):
        """Return kwargs to be passed to the create_download method."""
        return {}

    def get_form_data(self):
        """If form class is not None return form.cleaned_data, else return None."""
        if self.form_class is None:
            return None
        form = self.form_class(self.request.POST)
        if form.is_valid():
            return form.cleaned_data
        else:
            raise Exception("Form not valid")

    def post(self, *args, **kwargs):
        """Create a new report download and return HTTP response."""
        try:
            form_data = self.get_form_data()
            create_download_kwargs = self.get_create_download_kwargs(form_data)
            self.model.objects.create_download(**create_download_kwargs)
        except Exception:
            return HttpResponseNotFound()
        else:
            return HttpResponse("ok")


class BaseReportStatus(ReportsUserMixin, TemplateView):
    """Base view for report request status."""

    template_name = "reports/report_status.html"
    model = None

    def get_report_download(self):
        """Return the report request to display."""
        return self.model.objects.filter(user=self.request.user).latest()

    def get_context_data(self, *args, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(*args, **kwargs)
        try:
            report = self.get_report_download()
        except self.model.DoesNotExist:
            report = None
        context["report_download"] = report
        return context


class ReorderReport(BaseReportPage):
    """View for viewing and exporting Re-Order reports."""

    template_name = "reports/report_page.html"
    report_name = "Reorder Report"
    form_class = forms.ReorderReportForm
    create_report_url = reverse_lazy("reports:create_reorder_report")
    report_list_url = reverse_lazy("reports:reorder_report_list")
    status_url = reverse_lazy("reports:reorder_report_status")


class CreateReorderReport(BaseCreateReport):
    """View for creating new reorder reports."""

    form_class = forms.ReorderReportForm
    model = models.ReorderReportDownload

    def get_create_download_kwargs(self, form_data):
        """Return kwargs to be passed to the create_download method."""
        return {
            "user": self.request.user,
            "supplier": form_data["supplier"],
            "date_from": form_data["date_from"],
            "date_to": form_data["date_to"],
        }


class ReorderReportList(BaseReportList):
    """View for reorder reports."""

    model = models.ReorderReportDownload
    template_name = "reports/reorder_report/report_list.html"


class ReorderReportStatus(BaseReportStatus):
    """View for reorder report status."""

    model = models.ReorderReportDownload
