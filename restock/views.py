"""Views for the restock app."""

from collections import defaultdict

from django.db import transaction
from django.db.models import Q
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import (
    CreateView,
    DeleteView,
    ListView,
    TemplateView,
    UpdateView,
    View,
)

from fba.models import FBAOrder
from home.views import UserInGroupMixin
from inventory.models import BaseProduct, Supplier
from restock import forms, models


class RestockUserMixin(UserInGroupMixin):
    """Mixin to validate user in in inventory group."""

    groups = ["restock"]


def sort_products_by_supplier(products):
    """Return a dict of {supplier:[products]}."""
    suppliers = defaultdict(list)
    for product in products:
        add_details_to_product(product)
        suppliers[product.supplier].append(product)
    return dict(suppliers)


class RestockView(RestockUserMixin, TemplateView):
    """View for the restock page."""

    template_name = "restock/restock.html"


def add_details_to_product(product):
    """Add fba order count and last reorder to product objects."""
    product.fba_order_count = (
        FBAOrder.objects.awaiting_fulfillment().filter(product=product).count()
    )
    product.last_reorder = models.Reorder.objects.last_reorder(product)


class SearchResults(RestockUserMixin, TemplateView):
    """View for restock page search results."""

    RESULT_LIMIT = 150

    template_name = "restock/restock_list_display.html"

    def get_context_data(self, *args, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(*args, **kwargs)
        search_text = self.request.GET["product_search"]
        products, context["result_count"] = self.get_products(search_text)
        context["result_limit"] = self.RESULT_LIMIT
        products = products[: self.RESULT_LIMIT]
        context["suppliers"] = sort_products_by_supplier(products)
        reorders = models.Reorder.objects.filter(product__in=products).open()
        context["reorder_counts"] = {}
        context["comments"] = {}
        for reorder in reorders:
            context["reorder_counts"][reorder.product.id] = reorder.count
            context["comments"][reorder.product.id] = reorder.comment
        return context

    def get_products(self, search_text):
        """Return products matching the search string."""
        search_terms = [_.strip() for _ in search_text.split() if _.strip()]
        qs = (
            BaseProduct.objects.complete()
            .active()
            .filter(
                Q(sku__in=search_terms)
                | Q(supplier_sku__in=search_terms)
                | Q(barcode__in=search_terms)
            )
            .distinct()
            .select_related("supplier")
            .order_by("supplier__name")
        )
        return qs[: self.RESULT_LIMIT], qs.count()


class RestockList(RestockUserMixin, TemplateView):
    """View for displaying products marked for restock."""

    template_name = "restock/restock_list.html"

    def get_context_data(self, *args, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(*args, **kwargs)
        supplier_ids = (
            models.Reorder.objects.open()
            .values_list("product__supplier", flat=True)
            .distinct()
        )
        context["suppliers"] = Supplier.objects.filter(pk__in=supplier_ids)
        return context


class SupplierRestockList(RestockUserMixin, TemplateView):
    """View for displaying products marked for restock."""

    template_name = "restock/supplier_restock_list.html"

    def get_context_data(self, *args, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(*args, **kwargs)
        supplier = get_object_or_404(Supplier, pk=self.kwargs["supplier_pk"])
        reorders = models.Reorder.objects.open().select_related(
            "product", "product__supplier"
        )
        product_ids = reorders.values_list("product__id", flat=True)
        products = models.BaseProduct.objects.filter(
            id__in=product_ids, supplier=supplier
        )
        for product in products:
            add_details_to_product(product)
        context["suppliers"] = {supplier: products}
        context["reorder_counts"] = {}
        context["comments"] = {}
        for reorder in reorders:
            context["reorder_counts"][reorder.product_id] = reorder.count
            context["comments"][reorder.product_id] = reorder.comment
        return context


@method_decorator(csrf_exempt, name="dispatch")
class UpdatePurchasePrice(RestockUserMixin, View):
    """View for handling purchase price updates from the restock page."""

    def post(self, *args, **kwargs):
        """Update purchase price."""
        try:
            updated_purchase_price = self.update_purchase_price()
        except Exception:
            return HttpResponseBadRequest()
        else:
            return JsonResponse({"purchase_price": updated_purchase_price})

    def update_purchase_price(self):
        """Update purchase price."""
        product_id = self.request.POST["product_id"]
        updated_purchase_price = self.request.POST["updated_purchase_price"]
        product = get_object_or_404(BaseProduct, id=product_id)
        with transaction.atomic():
            product.purchase_price = updated_purchase_price
            product.full_clean()
            product.save()
        return product.purchase_price


@method_decorator(csrf_exempt, name="dispatch")
class UpdateOrderCount(RestockUserMixin, View):
    """View for setting re-order counts."""

    def post(self, *args, **kwargs):
        """Update re-order counts."""
        try:
            updated_count = self.update_order_count()
        except Exception:
            return HttpResponseBadRequest()
        else:
            return JsonResponse({"count": updated_count})

    def update_order_count(self):
        """Update re-order count."""
        product_id = self.request.POST["product_id"]
        count = int(self.request.POST["updated_order_count"])
        product = get_object_or_404(BaseProduct, id=product_id)
        return models.Reorder.objects.set_count(product, count)


@method_decorator(csrf_exempt, name="dispatch")
class SetOrderComment(RestockUserMixin, View):
    """View for setting re-order comments."""

    def post(self, *args, **kwargs):
        """Update re-order comment."""
        try:
            comment = self.update_order_comment()
        except Exception:
            return HttpResponseBadRequest()
        else:
            return JsonResponse({"comment": comment})

    def update_order_comment(self):
        """Update re-order comment."""
        product_id = self.request.POST["product_id"]
        comment = self.request.POST["comment"]
        product = get_object_or_404(BaseProduct, id=product_id)
        return models.Reorder.objects.set_comment(product, comment)


@method_decorator(csrf_exempt, name="dispatch")
class SetSupplierComment(RestockUserMixin, View):
    """View for setting supplier re-order comments."""

    def post(self, *args, **kwargs):
        """Update re-order comment."""
        try:
            comment = self.update_supplier_comment()
        except Exception:
            return HttpResponseBadRequest()
        else:
            return JsonResponse({"comment": comment})

    def update_supplier_comment(self):
        """Update re-order comment."""
        supplier_id = self.request.POST["supplier_id"]
        comment = self.request.POST["comment"]
        supplier = get_object_or_404(Supplier, id=supplier_id)
        supplier.restock_comment = comment
        supplier.save()
        return supplier.restock_comment


class BrandBlacklist(RestockUserMixin, ListView):
    """View for displaying the list of blacklisted brands."""

    model = models.BlacklistedBrand
    template_name = "restock/blacklistedbrand_list.html"

    def get_queryset(self, *args, **kwargs):
        """Perform fuzzy search if search text is in GET."""
        if search_text := self.request.GET.get("search_text"):
            return self.model.objects.fuzzy_search(search_text)
        else:
            return super().get_queryset()


class CreateBlacklistedBrand(RestockUserMixin, CreateView):
    """View for creating blacklisted brands."""

    model = models.BlacklistedBrand
    fields = ("name", "comment")
    success_url = reverse_lazy("restock:brand_blacklist")


class UpdateBlacklistedBrand(RestockUserMixin, UpdateView):
    """View for updating blacklisted brands."""

    model = models.BlacklistedBrand
    fields = ("name", "comment")
    success_url = reverse_lazy("restock:brand_blacklist")


class DeleteBlacklistedBrand(RestockUserMixin, DeleteView):
    """View for deleting blacklisted brands."""

    model = models.BlacklistedBrand
    success_url = reverse_lazy("restock:brand_blacklist")


class UpdateLastOrderedDate(RestockUserMixin, UpdateView):
    """View for updating the last order date of suppliers."""

    model = Supplier
    form_class = forms.UpdateSuplierOrderDateForm
    template_name = "restock/update_supplier_last_ordered.html"
