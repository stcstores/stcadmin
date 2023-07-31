"""Views for the purchases app."""

from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, TemplateView, View
from django.views.generic.edit import DeleteView, FormView, UpdateView

from home.models import Staff
from home.views import UserInGroupMixin
from inventory.models import BaseProduct
from purchases import forms, models


class PurchasesUserMixin(UserInGroupMixin):
    """Mixin to validate user in in purchases group."""

    groups = ["purchases", "purchase_manager"]


class ProductSearch(PurchasesUserMixin, TemplateView):
    """View for searching for products to purchase."""

    template_name = "purchases/product_search.html"

    def get_context_data(self, *args, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(*args, **kwargs)
        context["form"] = forms.ProductSearchForm()
        return context


class ProductSearchResults(PurchasesUserMixin, ListView):
    """AJAX view for displaying product search results."""

    model = BaseProduct
    paginate_by = 50
    template_name = "purchases/product_search_results.html"

    def get_queryset(self):
        """Return product queryset."""
        form = forms.ProductSearchForm(self.request.GET)
        return form.get_queryset()


class CreatePurchase(PurchasesUserMixin, FormView):
    """View for creating new purchases."""

    form_class = forms.CreatePurchaseForm
    template_name = "purchases/create_purchase.html"
    success_url = reverse_lazy("purchases:product_search")

    def get_initial(self):
        """Return initial values for the form."""
        initial = super().get_initial()
        initial["product_id"] = self.kwargs["product_pk"]
        initial["purchaser"] = self.request.user.staff_member.id
        return initial

    def get_context_data(self, *args, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(*args, **kwargs)
        context["product"] = get_object_or_404(
            BaseProduct, pk=self.kwargs["product_pk"]
        )
        purchase_charge = models.PurchaseSettings.get_solo().purchase_charge
        context["to_pay"] = context["product"].purchase_price * purchase_charge
        return context

    def form_valid(self, form):
        """Create a new purchase."""
        form.save()
        return super().form_valid(form)


class ManagePurchases(PurchasesUserMixin, TemplateView):
    """View for managing purchases."""

    template_name = "purchases/manage_purchases.html"

    def get_context_data(self, *args, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(*args, **kwargs)
        staff_ids = (
            models.Purchase.objects.filter(export__isnull=True)
            .values_list("purchased_by", flat=True)
            .distinct()
        )
        context["purchasers"] = Staff.objects.filter(id__in=staff_ids)
        return context


class ManageUserPurchases(PurchasesUserMixin, TemplateView):
    """View for managing user purchaes."""

    template_name = "purchases/manage_user_purchases.html"

    def get_context_data(self, *args, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(*args, **kwargs)
        purchaser = get_object_or_404(Staff, pk=self.kwargs["staff_pk"])
        context["purchaser"] = purchaser
        context["purchases"] = models.Purchase.objects.filter(
            purchased_by=purchaser, export__isnull=True
        ).order_by("-created_at")
        context["total_to_pay"] = round(
            sum((_.to_pay() for _ in context["purchases"])), 2
        )
        return context


class UpdatePurchase(PurchasesUserMixin, UpdateView):
    """View for updating purchases."""

    model = models.Purchase
    fields = ("quantity",)
    template_name = "purchases/update_purchase.html"
    queryset = models.Purchase.objects.filter(export__isnull=True)

    def get_success_url(self):
        """Return the success URL."""
        return reverse(
            "purchases:manage_user_purchases",
            kwargs={"staff_pk": self.object.purchased_by.pk},
        )


class DeletePurchase(PurchasesUserMixin, DeleteView):
    """View for deleting purchases."""

    model = models.Purchase
    queryset = models.Purchase.objects.filter(export__isnull=True)
    success_url = reverse_lazy("purchases:manage_purchases")


class PurchaseReports(PurchasesUserMixin, ListView):
    """View for listing purchase reports."""

    model = models.PurchaseExport
    paginate_by = 50
    template_name = "purchases/purchase_reports.html"


class DownloadPurchaseReport(PurchasesUserMixin, View):
    """View for downloading purchase reports."""

    def get(self, *args, **kwargs):
        """Download a purchase report .csv file."""
        export = get_object_or_404(models.PurchaseExport, pk=self.kwargs["pk"])
        report = export.generate_report().getvalue()
        filename = self.get_filename(export)
        response = HttpResponse(report)
        response["Content-Disposition"] = f"attachment;filename={filename}"
        return response

    @staticmethod
    def get_filename(export):
        """Return the filename for the report."""
        return f"purchase_report_{export.export_date.strftime('%b_%Y')}.csv"
