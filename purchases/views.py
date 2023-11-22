"""Views for the purchases app."""

from django.conf import settings
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView, TemplateView, View
from django.views.generic.edit import DeleteView, FormView, UpdateView

from home.models import Staff
from home.views import UserInGroupMixin
from inventory.models import BaseProduct
from purchases import forms, models
from shipping.models import Country


class PurchasesUserMixin(UserInGroupMixin):
    """Mixin to validate user in in purchases group."""

    groups = ["purchases", "purchase_manager"]


class Index(PurchasesUserMixin, TemplateView):
    """View for the purchases index page."""

    template_name = "purchases/index.html"


class ProductSearch(PurchasesUserMixin, ListView):
    """View for searching for products to purchase."""

    template_name = "purchases/product_search.html"
    form_class = forms.ProductSearchForm
    model = BaseProduct
    paginate_by = 50

    def get_queryset(self):
        """Return a queryset of product ranges filtered by the request's GET params."""
        form = self.form_class(self.request.GET)
        form.is_valid()
        return form.get_queryset()

    def get_context_data(self, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(**kwargs)
        context["form"] = self.form_class(self.request.GET)
        return context


class CreateProductPurchase(PurchasesUserMixin, FormView):
    """View for creating new product purchases."""

    form_class = forms.CreateProductPurchaseForm
    template_name = "purchases/create_product_purchase.html"
    success_url = reverse_lazy("purchases:index")

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
        self.update_stock_level(form)
        return super().form_valid(form)

    def update_stock_level(self, form):
        """Update product stock level."""
        if settings.DEBUG is True:
            messages.add_message(
                self.request,
                messages.WARNING,
                "Purchase created. DEBUG: Stock Update Skipped",
            )
        else:
            try:
                new_stock_level = form.update_stock_level()
            except Exception:
                messages.add_message(
                    self.request,
                    messages.ERROR,
                    f"Purchase created. Failed to reduce stock level by {form.instance.quantity} for "
                    f"{form.instance.product.sku} - {form.instance.product.full_name}",
                )
            else:
                messages.add_message(
                    self.request,
                    messages.SUCCESS,
                    f"Purchase created. Stock level set to {new_stock_level}",
                )


class CreateShippingPurchase(PurchasesUserMixin, FormView):
    """View for creating new shipping purchases."""

    form_class = forms.CreateShippingPurchaseForm
    template_name = "purchases/create_shipping_purchase.html"
    success_url = reverse_lazy("purchases:index")

    def get_initial(self):
        """Return initial values for the form."""
        initial = super().get_initial()
        initial["purchaser"] = self.request.user.staff_member.id
        initial["country"] = Country.objects.get(name="United Kingdom")
        return initial

    def form_valid(self, form):
        """Create a new purchase."""
        form.save()
        messages.add_message(self.request, messages.SUCCESS, "Purchase created.")
        return super().form_valid(form)


class CreateOtherPurchase(PurchasesUserMixin, FormView):
    """View for creating new other purchases."""

    form_class = forms.CreateOtherPurchaseForm
    template_name = "purchases/create_other_purchase.html"
    success_url = reverse_lazy("purchases:index")

    def get_initial(self):
        """Return initial values for the form."""
        initial = super().get_initial()
        initial["purchaser"] = self.request.user.staff_member.id
        return initial

    def form_valid(self, form):
        """Create a new purchase."""
        form.save()
        messages.add_message(self.request, messages.SUCCESS, "Purchase created.")
        return super().form_valid(form)


class UpdateProductPurchase(PurchasesUserMixin, UpdateView):
    """View for updating product purchases."""

    model = models.ProductPurchase
    form_class = forms.UpdateProductPurchaseForm
    template_name = "purchases/update_product_purchase.html"
    queryset = models.ProductPurchase.objects.filter(export__isnull=True)

    def form_valid(self, form):
        """Update purchase and stock level."""
        form.save()
        self.update_stock_level(form)
        return HttpResponseRedirect(self.get_success_url())

    def update_stock_level(self, form):
        """Update product stock level."""
        if settings.DEBUG is True:
            messages.add_message(
                self.request, messages.WARNING, "DEBUG: Stock Update Skipped"
            )
        else:
            try:
                new_stock_level = form.update_stock_level()
            except Exception:
                messages.add_message(
                    self.request,
                    messages.ERROR,
                    "Failed to update stock level for "
                    f"{form.instance.product.sku} - {form.instance.product.full_name}",
                )
            else:
                messages.add_message(
                    self.request,
                    messages.SUCCESS,
                    f"Purchase updated. Stock level set to {new_stock_level}",
                )

    def get_success_url(self):
        """Return the success URL."""
        return reverse(
            "purchases:manage_user_purchases",
            kwargs={"staff_pk": self.object.purchased_by.pk},
        )


class UpdateShippingPurchase(PurchasesUserMixin, UpdateView):
    """View for updating shipping purchases."""

    model = models.ShippingPurchase
    fields = ["quantity"]
    template_name = "purchases/update_shipping_purchase.html"
    queryset = models.ShippingPurchase.objects.filter(export__isnull=True)

    def get_success_url(self):
        """Return the success URL."""
        return reverse(
            "purchases:manage_user_purchases",
            kwargs={"staff_pk": self.object.purchased_by.pk},
        )


class UpdateOtherPurchase(PurchasesUserMixin, UpdateView):
    """View for updating other purchases."""

    model = models.OtherPurchase
    fields = ["description", "quantity", "price"]
    template_name = "purchases/update_other_purchase.html"
    queryset = models.OtherPurchase.objects.filter(export__isnull=True)

    def get_success_url(self):
        """Return the success URL."""
        return reverse(
            "purchases:manage_user_purchases",
            kwargs={"staff_pk": self.object.purchased_by.pk},
        )


class ManagePurchases(PurchasesUserMixin, TemplateView):
    """View for managing purchases."""

    template_name = "purchases/manage_purchases.html"

    def get_context_data(self, *args, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(*args, **kwargs)
        staff_ids = (
            models.BasePurchase.objects.filter(export__isnull=True)
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
        context["purchases"] = models.BasePurchase.objects.filter(
            purchased_by=purchaser, export__isnull=True
        ).order_by("-created_at")
        context["total_to_pay"] = round(
            sum((_.to_pay() for _ in context["purchases"])), 2
        )
        return context


class DeletePurchase(PurchasesUserMixin, DeleteView):
    """View for deleting purchases."""

    model = models.BasePurchase
    queryset = models.BasePurchase.objects.filter(export__isnull=True)
    template_name = "purchases/purchase_confirm_delete.html"
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
        filename = export.get_report_filename()
        response = HttpResponse(report)
        response["Content-Disposition"] = f"attachment;filename={filename}"
        return response
