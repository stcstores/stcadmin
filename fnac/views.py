"""Views for the fnac app."""

from django import http
from django.http import HttpResponse, JsonResponse
from django.shortcuts import reverse
from django.views import View
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView, UpdateView

from fnac import forms, models
from home.views import UserInGroupMixin

from .tasks import (
    create_missing_information_export,
    create_new_product_export,
    create_offer_update_export,
    update_inventory,
)


class FnacUserMixin(UserInGroupMixin):
    """View mixin to ensure user is in the fnac group."""

    groups = ["fnac"]


class Index(FnacUserMixin, TemplateView):
    """Index view for the fnac app."""

    template_name = "fnac/index.html"

    def get_context_data(self, *args, **kwargs):
        """Return template context data."""
        context = super().get_context_data(*args, **kwargs)
        to_be_created = models.FnacProduct.objects.to_be_created()
        context["created_product_count"] = self.created_product_count()
        context["invalid_in_inventory_count"] = self.invalid_in_inventory_count(
            to_be_created
        )
        context["missing_information_count"] = self.missing_information_count(
            to_be_created
        )
        context["do_not_create_count"] = self.do_not_create_count()
        context["out_of_stock_count"] = self.out_of_stock_count()
        context["missing_translations_count"] = self.missing_translations_count(
            to_be_created
        )
        context["ready_to_create_count"] = self.ready_to_create_count()
        return context

    def created_product_count(self):
        """Return the number of products that have been created."""
        return models.FnacProduct.objects.filter(created=True).count()

    def invalid_in_inventory_count(self, to_be_created):
        """Return the number of products with invalid inventory information."""
        return to_be_created.intersection(
            models.FnacProduct.objects.invalid_in_inventory()
        ).count()

    def missing_information_count(self, to_be_created):
        """Return the number of products without categories."""
        return (
            to_be_created.intersection(models.FnacProduct.objects.missing_information())
        ).count()

    def do_not_create_count(self):
        """Return the number of products marked do not create."""
        return models.FnacProduct.objects.filter(do_not_create=True).count()

    def out_of_stock_count(self):
        """Return the number of products that are out of stock."""
        return (
            models.FnacProduct.objects.not_do_not_create()
            & models.FnacProduct.objects.out_of_stock()
        ).count()

    def missing_translations_count(self, to_be_created):
        """Return the number of products that are missing translation information."""
        return to_be_created.intersection(
            models.FnacProduct.objects.not_translated()
        ).count()

    def ready_to_create_count(self):
        """Return the number of products that are ready to be created."""
        return models.FnacProduct.objects.ready_to_create().count()


class InvalidInInventory(FnacUserMixin, TemplateView):
    """View for displaying products that are not listed on FNAC due to invalid inventory info."""

    template_name = "fnac/invalid_in_inventory.html"

    def get_context_data(self, *args, **kwargs):
        """Return template context."""
        context = super().get_context_data(*args, **kwargs)
        context["products"] = models.FnacProduct.objects.invalid_in_inventory()
        return context


class Translations(FnacUserMixin, FormView):
    """View for updating translations."""

    template_name = "fnac/translations.html"
    form_class = forms.TranslationsForm

    def get_context_data(self, *args, **kwargs):
        """Return template context data."""
        context = super().get_context_data(*args, **kwargs)
        context[
            "missing_translations_count"
        ] = models.FnacProduct.objects.not_translated().count()
        return context

    def form_valid(self, form):
        """Create new translations."""
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        """Return the URL to redirect to if forms submission is successful."""
        return reverse("fnac:index")


class TranslationsExport(FnacUserMixin, View):
    """Download an XLSX file for translation."""

    def get(*args, **kwargs):
        """Return an HttpResponse object with the XLSX export."""
        export_file = models.Translation.objects.translations_export()
        response = http.HttpResponse(
            export_file,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sh",
        )
        response["Content-Disposition"] = 'attachment; filename="to_translate.xlsx"'
        return response


class ShippingComment(FnacUserMixin, UpdateView):
    """View for the Shipping Comment."""

    template_name = "fnac/shipping_comment.html"
    model_class = models.Comment
    fields = ("comment",)

    def get_object(self):
        """Return kwargs for the form."""
        return self.model_class.objects.get_comment()

    def form_valid(self, form):
        """Create new translations."""
        models.Comment.objects.set_comment_text(form.cleaned_data["comment"])
        return super().form_valid(form)

    def get_success_url(self):
        """Return the URL to redirect to if forms submission is successful."""
        return reverse("fnac:index")


class CreatedProducts(FnacUserMixin, FormView):
    """View for uploading Mirak product exports to mark created products."""

    template_name = "fnac/created_products.html"
    form_class = forms.CreatedProductsForm

    def form_valid(self, form):
        """Mark created products."""
        form.save()
        return super().form_valid(form)

    def get_success_url(self):
        """Return the URL to redirect to if forms submission is successful."""
        return reverse("fnac:index")


class MissingInformation(FnacUserMixin, TemplateView):
    """View for downloading missing information exports."""

    template_name = "fnac/missing_information.html"

    def get_context_data(self, **kwargs):
        """Return the context for the template."""
        context = super().get_context_data(**kwargs)
        context["form"] = forms.MissingInformationUploadForm()
        context["MissingInformationImport"] = models.MissingInformationImport
        return context


class CreateMissingInformationExport(FnacUserMixin, View):
    """View to trigger the creation of a missing information export."""

    def get(self, *args, **kwargs):
        """Trigger the creation of a missing information export."""
        create_missing_information_export.delay()
        return HttpResponse("done")


class MissingInformationExportStatus(FnacUserMixin, TemplateView):
    """View to provide the status of the latest information export for ajax."""

    template_name = "fnac/missing_information_export_status.html"

    def get_context_data(self, *args, **kwargs):
        """Return the context for the template."""
        context = super().get_context_data(*args, **kwargs)
        try:
            context["export"] = models.MissingInformationExport.objects.latest(
                "timestamp"
            )
        except models.MissingInformationExport.DoesNotExist:
            context["export"] = None
        context[
            "in_progress"
        ] = models.MissingInformationExport.objects.is_in_progress()
        return context


class StartMissingInformationImport(FnacUserMixin, View):
    """View to trigger the import of missing product information."""

    def post(self, *args, **kwargs):
        """Trigger the import of missing product information."""
        form = forms.MissingInformationUploadForm(
            data=self.request.POST, files=self.request.FILES
        )
        if form.is_valid():
            form.save()
            return HttpResponse("done")
        return HttpResponse(status=500)


class MissingInformationImportStatus(FnacUserMixin, View):
    """View to provide the status of the latest information import for ajax."""

    def get_data(self):
        """Return view response data."""
        data = {"status": None, "latest": None}
        if models.MissingInformationImport.objects.is_in_progress():
            data["status"] = models.MissingInformationImport.IN_PROGRESS
            return data
        try:
            import_object = models.MissingInformationImport.objects.latest("timestamp")
        except models.MissingInformationImport.DoesNotExist:
            return data
        else:
            data["status"] = import_object.status
            data["latest"] = import_object.timestamp.strftime("%H:%M on %d %b %Y")
        return data

    def get(self, *args, **kwargs):
        """Return the import status as JSON."""
        return JsonResponse(self.get_data())


class StartInventoryUpdate(FnacUserMixin, View):
    """View to trigger an inventory update."""

    def get(self, *args, **kwargs):
        """Start an inventory update."""
        update_inventory.delay()
        return HttpResponse("done")


class InventoryUpdateStatus(FnacUserMixin, TemplateView):
    """Show the status of the current or most recent inventory update."""

    template_name = "fnac/inventory_import_status.html"

    def get_context_data(self, *args, **kwargs):
        """Return the context for the template."""
        context = super().get_context_data(*args, **kwargs)
        try:
            context["import"] = models.InventoryImport.objects.latest("timestamp")
        except models.InventoryImport.DoesNotExist:
            context["import"] = None
        context["in_progress"] = models.InventoryImport.objects.is_in_progress()
        return context


class CreateOfferUpdate(FnacUserMixin, View):
    """View to trigger the creation of an offer update export."""

    def get(self, *args, **kwargs):
        """Trigger the creation of an offer update export."""
        create_offer_update_export.delay()
        return HttpResponse("done")


class OfferUpdateStatus(FnacUserMixin, TemplateView):
    """View to provide the status of the latest information export for ajax."""

    template_name = "fnac/offer_update_status.html"

    def get_context_data(self, *args, **kwargs):
        """Return the context for the template."""
        context = super().get_context_data(*args, **kwargs)
        try:
            context["export"] = models.OfferUpdate.objects.latest("timestamp")
        except models.OfferUpdate.DoesNotExist:
            context["export"] = None
        context["in_progress"] = models.OfferUpdate.objects.is_in_progress()
        return context


class CreateNewProductExport(FnacUserMixin, View):
    """View to trigger the creation of a new product export."""

    def get(self, *args, **kwargs):
        """Trigger the creation of a new product export."""
        create_new_product_export.delay()
        return HttpResponse("done")


class NewProductExportStatus(FnacUserMixin, TemplateView):
    """View to provide the status of the latest new product export for ajax."""

    template_name = "fnac/new_product_export_status.html"

    def get_context_data(self, *args, **kwargs):
        """Return the context for the template."""
        context = super().get_context_data(*args, **kwargs)
        try:
            context["export"] = models.NewProductExport.objects.latest("timestamp")
        except models.NewProductExport.DoesNotExist:
            context["export"] = None
        context["in_progress"] = models.NewProductExport.objects.is_in_progress()
        return context
