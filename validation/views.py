"""Validation views."""

from django.views.generic.base import TemplateView

from home.views import UserInGroupMixin
from validation import models
from validation.levels import Levels


class ValidationUserMixin(UserInGroupMixin):
    """Mixin to validate user in in validation group."""

    groups = ["validation"]


class BaseValidationList(ValidationUserMixin, TemplateView):
    """Base view class for lists of validation errors."""

    def get_context_data(self, *args, **kwargs):
        """Return context for the template."""
        context = super().get_context_data()
        context["errors"] = self.error_data(self.group_by)
        return context

    def error_stats(self, errors):
        """Return stats for a list of validation errors."""
        stats = {"levels": {_: 0 for _ in Levels.all()}, "total": 0}
        for error in errors:
            stats["levels"][error.level()] += 1
            stats["total"] += 1
        return stats

    def error_data(self, group_attribute):
        """Return validation error data."""
        errors = self.errors()
        object_validator_names = errors.values_list(group_attribute, flat=True)
        error_data = {}
        for name in object_validator_names:
            object_data = {}
            object_errors = [_ for _ in errors if getattr(_, group_attribute) == name]
            object_data["errors"] = object_errors
            object_data["stats"] = self.error_stats(object_errors)
            error_data[name] = object_data
        return error_data


class Home(BaseValidationList):
    """Landing page for the validation app."""

    template_name = "validation/home.html"
    group_by = "app"

    def get_context_data(self, *args, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(*args, **kwargs)
        context["apps"] = (
            models.ModelValidationLog.objects.order_by()
            .values_list("app", flat=True)
            .distinct()
        )
        return context

    def errors(self):
        """Return applicable validation errors."""
        return models.ModelValidationLog.objects.order_by(
            "-error_level", "validation_check", "error_message"
        ).all()


class App(BaseValidationList):
    """Validation errors for an app."""

    template_name = "validation/app.html"
    group_by = "model"

    def get_context_data(self, *args, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(*args, **kwargs)
        context["app"] = self.kwargs["app"]
        return context

    def errors(self):
        """Return applicable validation errors."""
        return models.ModelValidationLog.objects.filter(
            app=self.kwargs["app"]
        ).order_by("-error_level", "validation_check", "error_message")


class Model(BaseValidationList):
    """Validation errors for a database model."""

    template_name = "validation/model.html"
    group_by = "object_validator"

    def get_context_data(self, *args, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(*args, **kwargs)
        context["app"] = self.kwargs["app"]
        context["model"] = self.kwargs["model"]
        return context

    def errors(self):
        """Return applicable validation errors."""
        return models.ModelValidationLog.objects.filter(
            app=self.kwargs["app"], model=self.kwargs["model"]
        ).order_by(
            "-error_level", "object_validator", "validation_check", "error_message"
        )
