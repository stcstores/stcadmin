"""Views for the Purchases app."""

import json

from ccapi import CCAPI
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView, TemplateView

from home.views import UserInGroupMixin
from purchases import forms, models


class PurchaseUserMixin(UserInGroupMixin):
    """View mixin to ensure user is in the purchase group."""

    groups = ["purchase"]


class PurchaseManagerUserMixin(UserInGroupMixin):
    """View mixin to ensure user is in the purchase_manager group."""

    groups = ["purchase", "purchase_manager"]


class Purchase(PurchaseManagerUserMixin, TemplateView):
    """View for creating new purchases."""

    template_name = "purchases/purchase.html"


class Manage(PurchaseManagerUserMixin, TemplateView):
    """View for managing purchases."""

    template_name = "purchases/manage.html"


class PurchaseFromStock(PurchaseManagerUserMixin, FormView):
    """View for creating stock purchases."""

    form_class = forms.PurchaseFromStock
    template_name = "purchases/from_stock.html"

    def form_valid(self, form):
        """Handle completed form."""
        user = form.cleaned_data["purchaser"]
        stock_purchases = []
        for product in json.loads(form.cleaned_data["basket"]):
            purchase_price = int(float(product["purchase_price"]) * 100)
            to_pay = purchase_price * product["quantity"] * 2
            purchase = models.StockPurchase(
                user=user,
                to_pay=to_pay,
                product_id=product["product_id"],
                product_sku=product["sku"],
                product_name=product["name"],
                product_purchase_price=purchase_price,
                quantity=product["quantity"],
            )
            stock_purchases.append(purchase)
        with transaction.atomic():
            for purchase in stock_purchases:
                purchase.save()
        return super().form_valid(form)


@method_decorator(csrf_exempt, name="dispatch")
class ProductSearch(PurchaseManagerUserMixin, View):
    """View for product searches."""

    def get(self, *args, **kwargs):
        """Process HTTP request."""
        search_text = self.request.GET.get("search_text")
        channel_id = self.request.GET.get("channel_id")
        products = self.do_search(search_text=search_text, channel_id=channel_id)
        data = self._product_search_result_to_dict(products)
        return JsonResponse(data, safe=False)

    def _product_search_result_to_dict(self, search_result):
        return [
            {
                "product_id": result.variation_id,
                "name": result.name,
                "sku": result.sku,
                "thumbnail": result.thumbnail,
            }
            for result in search_result
        ]


class SearchProductName(ProductSearch):
    """Return a list of products by name."""

    def do_search(self, search_text, channel_id):
        """Return product search results."""
        return CCAPI.search_product_name(search_text, channel_id=channel_id)


class SearchProductSKU(ProductSearch):
    """Return a list of products by SKU."""

    def do_search(self, search_text, channel_id):
        """Return product search results."""
        return CCAPI.search_product_SKU(search_text, channel_id=channel_id)


@method_decorator(csrf_exempt, name="dispatch")
class ProductPurchasePrice(PurchaseManagerUserMixin, View):
    """View for product purchase price requests."""

    def get(self, *args, **kwargs):
        """Process HTTP request."""
        product_id = self.request.GET.get("product_id")
        product_options = CCAPI.get_options_for_product(product_id)
        purchase_price = product_options["Purchase Price"].value.value
        data = {"product_id": product_id, "purchase_price": purchase_price}
        return JsonResponse(data, safe=False)


class ManagePurchases(PurchaseManagerUserMixin, TemplateView):
    """View for purchase history."""

    template_name = "purchases/manage_purchases.html"

    def get_context_data(self, *args, **kwargs):
        """Return context for the view."""
        context = super().get_context_data()
        form = forms.PurchaseManagement(self.request.GET)
        user = None
        if form.is_valid():
            month = int(form.cleaned_data["month"])
            year = int(form.cleaned_data["year"])
            user = form.cleaned_data["user"]
        else:
            date = timezone.now()
            month = date.month
            year = date.year
            form = forms.PurchaseManagement(initial={"month": month, "year": year})
        context["purchases"] = models.Purchase.objects.filter(
            user=user, created_at__year=year, created_at__month=month
        )
        context["form"] = form
        return context


@method_decorator(csrf_exempt, name="dispatch")
class MarkOrderPaid(View):
    """Mark a purchase as paid."""

    def post(self, *args, **kwargs):
        """Mark a purchase as paid."""
        purchase_id = self.request.POST.get("purchase_id")
        purchase = get_object_or_404(models.Purchase, pk=purchase_id)
        purchase.paid = True
        purchase.save()
        return JsonResponse({purchase_id: "ok"})
