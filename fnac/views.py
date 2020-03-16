"""Views for the fnac app."""

from django import http
from django.shortcuts import reverse
from django.views import View
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView

from fnac import forms, models
from home.views import UserInGroupMixin


class FnacUserMixin(UserInGroupMixin):
    """View mixin to ensure user is in the print audit group."""

    groups = ["fnac"]


class Index(FnacUserMixin, TemplateView):
    """Index view for the fnac app."""

    template_name = "fnac/index.html"

    def get_context_data(self, *args, **kwargs):
        """Return template context data."""
        context = super().get_context_data(*args, **kwargs)
        context["created_product_count"] = models.FnacProduct.objects.filter(
            created=True
        ).count()
        context[
            "missing_inventory_info_count"
        ] = models.FnacProduct.objects.missing_inventory_information().count()
        context[
            "missing_category_count"
        ] = models.FnacProduct.objects.missing_category().count()
        context["missing_price_size_count"] = (
            models.FnacProduct.objects.missing_price()
            | models.FnacProduct.objects.size_invalid()
        ).count()
        context["do_not_create_count"] = models.FnacProduct.objects.filter(
            do_not_create=True
        ).count()
        context["out_of_stock_count"] = models.FnacProduct.objects.filter(
            stock_level=0
        ).count()
        context[
            "missing_translations_count"
        ] = models.FnacProduct.objects.not_translated().count()
        context[
            "ready_to_create_count"
        ] = models.FnacProduct.objects.ready_to_create().count()
        return context


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
