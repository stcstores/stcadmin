"""Views for the fnac app."""

from django import http
from django.http import HttpResponse
from django.shortcuts import reverse
from django.views import View
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView, UpdateView

from fnac import forms, models
from home.views import UserInGroupMixin

from .tasks import create_missing_information_export


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
        context["missing_inventory_info_count"] = self.missing_inventory_info_count(
            to_be_created
        )
        context["missing_category_count"] = self.missing_category_count(to_be_created)
        context["missing_price_size_count"] = self.missing_price_size_count(
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

    def missing_inventory_info_count(self, to_be_created):
        """Return the number of products missing inventory information."""
        return to_be_created.intersection(
            models.FnacProduct.objects.missing_inventory_information()
        ).count()

    def missing_category_count(self, to_be_created):
        """Return the number of products without categories."""
        return (to_be_created & models.FnacProduct.objects.missing_category()).count()

    def missing_price_size_count(self, to_be_created):
        """Return the number of products missing size or price information."""
        return to_be_created.intersection(
            models.FnacProduct.objects.missing_price().union(
                models.FnacProduct.objects.size_invalid()
            )
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


class MissingInventoryInfo(FnacUserMixin, TemplateView):
    """View for displaying products that are not listed on FNAC due to missing inventory info."""

    template_name = "fnac/missing_inventory_info.html"

    def get_context_data(self, *args, **kwargs):
        """Return template context."""
        context = super().get_context_data(*args, **kwargs)
        context["products"] = models.FnacProduct.objects.missing_inventory_information()
        return context


class MissingPriceSize(FnacUserMixin, FormView):
    """View for displaying products that cannot be listed on FNAC because they do not have a price."""

    template_name = "fnac/missing_prices.html"
    form_class = forms.MissingPriceSizeFormset

    def form_valid(self, formset):
        """Save forms and redirect."""
        for form in formset:
            form.save()
        return super().form_valid(formset)

    def get_success_url(self):
        """Return the URL to redirect to if forms submission is successful."""
        return reverse("fnac:index")


class MissingCategory(FnacUserMixin, FormView):
    """View for displaying products that are missing a category."""

    template_name = "fnac/missing_category.html"
    form_class = forms.MissingCategoryFormset

    def form_valid(self, formset):
        """Save forms and redirect."""
        for form in formset:
            form.save()
        return super().form_valid(formset)

    def get_success_url(self):
        """Return the URL to redirect to if forms submission is successful."""
        return reverse("fnac:index")


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


class NewProductFile(FnacUserMixin, View):
    """View for exporting new product import files for FNAC."""

    def get(*args, **kwargs):
        """Return an HttpResponse object with the XLSX export."""
        export_file = models.create_new_product_upload()
        response = http.HttpResponse(
            export_file,
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sh",
        )
        response["Content-Disposition"] = 'attachment; filename="mirakl_products.xlsx"'
        return response


class UpdateFile(FnacUserMixin, View):
    """View for exporting stock and price update files."""

    def get(*args, **kwargs):
        """Return an HttpResponse object with the CSV export."""
        export_file = models.create_update_upload()
        response = http.HttpResponse(export_file.getvalue(), content_type="text/csv")
        response["Content-Disposition"] = 'attachment; filename="FNAC_offers.csv"'
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


class CreateMissingInformationExport(FnacUserMixin, View):
    """View to trigger the creation of a missing information export."""

    def get(self, *args, **kwargs):
        """Trigger the creation of a missing information export."""
        create_missing_information_export.delay()
        return HttpResponse("done")


class MissingInformationExportStatus(FnacUserMixin, TemplateView):
    """View to provide the status of the latest information export for ajax."""

    template_name = "fnac/missing_information_export_status.html"

    def get_context_data(self, **kwargs):
        """Return the context for the template."""
        context = super().get_context_data(**kwargs)
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
