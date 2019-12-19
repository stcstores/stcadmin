"""Miscellaneous views for print audit app."""

from django.views.generic.base import TemplateView

from home.views import UserInGroupMixin


class PrintAuditUserMixin(UserInGroupMixin):
    """View mixin to ensure user is in the print audit group."""

    groups = ["print_audit"]


class Index(PrintAuditUserMixin, TemplateView):
    """View for print_audit hompage."""

    template_name = "print_audit/index.html"
