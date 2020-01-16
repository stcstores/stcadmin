from django.contrib.auth.models import Group

from stcadmin.tests.stcadmin_test import STCAdminTest, ViewTests
from validation import models
from validation.levels import Levels


class ValidationViewTest(STCAdminTest):
    group_name = "validation"

    def setUp(self):
        self.create_user()
        group, _ = Group.objects.get_or_create(name=self.group_name)
        group.user_set.add(self.user)
        self.login_user()

    def remove_group(self):
        super().remove_group(self.group_name)


class TestHomeView(ValidationViewTest, ViewTests):
    fixtures = ("validation/model_validation_log",)
    URL = "/validation/home/"
    template = "validation/home.html"

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)

    def test_context(self):
        response = self.make_get_request()
        self.assertIsNotNone(response.context)
        self.assertIn("errors", response.context)
        errors = response.context["errors"]
        self.assertIsInstance(errors, dict)
        for log in models.ModelValidationLog.objects.all():
            self.assertIn(log.app, errors)
            self.assertIsInstance(errors[log.app], dict)
            self.assertIn("errors", errors[log.app])
            self.assertIsInstance(errors[log.app]["errors"], list)
            self.assertIn(log, errors[log.app]["errors"])
        self.assertIn("stats", errors["inventory"])
        stats = errors["inventory"]["stats"]
        self.assertIsInstance(stats, dict)
        self.assertIn("levels", stats)
        self.assertIsInstance(stats["levels"], dict)
        for level in Levels.all():
            self.assertIn(level, stats["levels"])
            self.assertIsInstance(stats["levels"][level], int)
        self.assertIn("total", stats)
        self.assertIsInstance(stats["total"], int)
        self.assertEqual(stats["total"], models.ModelValidationLog.objects.count())
        self.assertIn("apps", response.context)
        self.assertEqual(["inventory"], list(response.context["apps"]))


class TestAppView(ValidationViewTest, ViewTests):
    fixtures = ("validation/model_validation_log",)

    template = "validation/app.html"

    def get_URL(self, app=None):
        if app is None:
            app = "inventory"
        return f"/validation/app/{app}/"

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)

    def test_context(self):
        response = self.make_get_request()
        self.assertIsNotNone(response.context)
        self.assertIn("errors", response.context)
        errors = response.context["errors"]
        self.assertIsInstance(errors, dict)
        for log in models.ModelValidationLog.objects.all():
            self.assertIn(log.model, errors)
            self.assertIsInstance(errors[log.model], dict)
            self.assertIn("errors", errors[log.model])
            self.assertIsInstance(errors[log.model]["errors"], list)
            self.assertIn(log, errors[log.model]["errors"])
        self.assertIn("stats", errors["Supplier"])
        stats = errors["Supplier"]["stats"]
        self.assertIsInstance(stats, dict)
        self.assertIn("levels", stats)
        self.assertIsInstance(stats["levels"], dict)
        for level in Levels.all():
            self.assertIn(level, stats["levels"])
            self.assertIsInstance(stats["levels"][level], int)
        self.assertIn("total", stats)
        self.assertIsInstance(stats["total"], int)
        self.assertEqual(stats["total"], models.ModelValidationLog.objects.count())
        self.assertIn("app", response.context)
        self.assertEqual("inventory", response.context["app"])


class TestModelView(ValidationViewTest, ViewTests):
    fixtures = ("validation/model_validation_log",)

    template = "validation/app.html"

    def get_URL(self, app=None, model=None):
        if app is None:
            app = "inventory"
        if model is None:
            model = "Supplier"
        return f"/validation/model/{app}/{model}/"

    def test_get_method(self):
        response = self.make_get_request()
        self.assertEqual(200, response.status_code)
        self.assertTemplateUsed(self.template)

    def test_context(self):
        response = self.make_get_request()
        self.assertIsNotNone(response.context)
        self.assertIn("errors", response.context)
        errors = response.context["errors"]
        self.assertIsInstance(errors, dict)
        for log in models.ModelValidationLog.objects.all():
            self.assertIn(log.object_validator, errors)
            self.assertIsInstance(errors[log.object_validator], dict)
            self.assertIn("errors", errors[log.object_validator])
            self.assertIsInstance(errors[log.object_validator]["errors"], list)
            self.assertIn(log, errors[log.object_validator]["errors"])
        self.assertIn("stats", errors["Factory"])
        stats = errors["Factory"]["stats"]
        self.assertIsInstance(stats, dict)
        self.assertIn("levels", stats)
        self.assertIsInstance(stats["levels"], dict)
        for level in Levels.all():
            self.assertIn(level, stats["levels"])
            self.assertIsInstance(stats["levels"][level], int)
        self.assertIn("total", stats)
        self.assertIsInstance(stats["total"], int)
        self.assertEqual(
            stats["total"],
            models.ModelValidationLog.objects.filter(
                object_validator="Factory"
            ).count(),
        )
        self.assertIn("app", response.context)
        self.assertEqual("inventory", response.context["app"])
        self.assertIn("model", response.context)
        self.assertEqual("Supplier", response.context["model"])
