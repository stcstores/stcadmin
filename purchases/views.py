"""Views for the Purchases app."""

import datetime
import json
from collections import defaultdict

from ccapi import CCAPI
from django.contrib import messages
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, reverse
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import FormView, TemplateView

from home.views import UserInGroupMixin, UserLoginMixin
from purchases import forms, models
from shipping.models import ShippingPrice


class PurchaserUserMixin(UserInGroupMixin):
    """View mixin to ensure user is in the purchaser group."""

    groups = ["purchaser"]


class PurchaseCreatorUserMixin(UserInGroupMixin):
    """View mixin to ensure user is in the purchase_creator group."""

    groups = ["purchase_creator"]


class PurchaseManagerUserMixin(UserInGroupMixin):
    """View mixin to ensure user is in the purchase_manager group."""

    groups = ["purchase_manager"]


class Purchase(UserLoginMixin, TemplateView):
    """View for creating new purchases."""

    template_name = "purchases/purchase.html"

    def get_user_purchases_for_month(self, month, year):
        """Return a queryset of purchases for the request user for a given month."""
        return models.Purchase.objects.filter(
            user=self.request.user,
            created_at__month=month,
            created_at__year=year,
        )

    def get_purchase_count(self, month, year):
        """Return a dict of user purchase counts for a given month."""
        queryset = models.Purchase.objects.filter(
            created_at__month=month,
            created_at__year=year,
        )
        purchase_counts = {}
        for purchase in queryset:
            if purchase.user not in purchase_counts:
                purchase_counts[purchase.user] = defaultdict(int)
            purchase_counts[purchase.user][purchase.__class__.__name__] += 1
            purchase_counts[purchase.user]["total"] += 1
        return purchase_counts

    def get_context_data(self, *args, **kwargs):
        """Return context for the view."""
        context = super().get_context_data()
        context["this_month"] = timezone.now().replace(day=1)
        context["last_month"] = context["this_month"] - datetime.timedelta(days=1)
        if self.request.user.groups.filter(name="purchaser").exists():
            context["this_month_purchases"] = self.get_user_purchases_for_month(
                context["this_month"].month, context["this_month"].year
            )
            context["last_month_purchases"] = self.get_user_purchases_for_month(
                context["last_month"].month, context["last_month"].year
            )
        if self.request.user.groups.filter(name="purchase_manager").exists():
            context["this_month_purchase_counts"] = self.get_purchase_count(
                context["this_month"].month, context["this_month"].year
            )
            context["last_month_purchase_counts"] = self.get_purchase_count(
                context["last_month"].month, context["last_month"].year
            )
        return context


class PurchaseView(TemplateView):
    """Base view for purchase lists."""

    def get_context_data(self, *args, **kwargs):
        """Return context for the view."""
        context = super().get_context_data()
        form = forms.PurchaseManagement(self.request.GET)
        if form.is_valid():
            month = int(form.cleaned_data["month"])
            year = int(form.cleaned_data["year"])
            if "user" in form.cleaned_data:
                self.user = form.cleaned_data["user"]
        else:
            date = timezone.now()
            month = date.month
            year = date.year
            form = forms.PurchaseManagement(initial={"month": month, "year": year})
        context["purchases"] = models.Purchase.objects.filter(
            user=self.user,
            created_at__year=year,
            created_at__month=month,
            cancelled=False,
        )
        total = sum([_.to_pay for _ in context["purchases"]]) / 100
        context["total"] = f"{total:.2f}"
        context["form"] = form
        return context


class ViewPurchases(PurchaserUserMixin, PurchaseView):
    """View for purchase history."""

    template_name = "purchases/view_purchases.html"

    def get_context_data(self, *args, **kwargs):
        """Return context for the view."""
        self.user = self.request.user
        context = super().get_context_data()
        del context["form"].fields["user"]
        return context


class ManagePurchases(PurchaseManagerUserMixin, PurchaseView):
    """View for purchase history."""

    template_name = "purchases/manage_purchases.html"

    def get_context_data(self, *args, **kwargs):
        """Return context for the view."""
        self.user = None
        context = super().get_context_data(*args, **kwargs)
        return context


class StockPurchase(PurchaseCreatorUserMixin, FormView):
    """Base view for product purchases."""

    form_class = forms.PurchaseFromStock

    def form_valid(self, form):
        """Handle completed form."""
        user = form.cleaned_data["purchaser"]
        discount_percentage = form.cleaned_data["discount"]
        basket = form.cleaned_data["basket"]
        self.add_purchases(
            user=user,
            basket=basket,
            discount_percentage=discount_percentage,
            profit_margin=form.profit_margin,
        )
        return super().form_valid(form)

    def get_success_url(self):
        """Return the sucess url."""
        return reverse("purchases:manage_purchases")


class PurchaseFromStock(StockPurchase):
    """View for creating stock purchases."""

    template_name = "purchases/from_stock.html"

    def add_purchases(self, basket, user, discount_percentage, profit_margin=0):
        """Add purchase to the database."""
        stock_purchases = []
        for product in json.loads(basket):
            purchase_price = int(float(product["purchase_price"]) * 100)
            total_price = purchase_price * product["quantity"] * profit_margin
            discount = total_price * (discount_percentage / 100)
            to_pay = int(total_price - discount)
            purchase = models.StockPurchase(
                user=user,
                to_pay=to_pay,
                created_by=self.request.user,
                product_id=product["product_id"],
                product_sku=product["sku"],
                product_name=product["name"],
                full_price=total_price,
                quantity=product["quantity"],
                discount_percentage=discount_percentage,
            )
            stock_purchases.append(purchase)
        with transaction.atomic():
            for purchase in stock_purchases:
                purchase.save()


class PurchaseFromShop(StockPurchase):
    """View for creating shop purchases."""

    template_name = "purchases/from_shop.html"

    def add_purchases(self, basket, user, discount_percentage, profit_margin=0):
        """Add purchase to the database."""
        product = json.loads(basket)
        quantity = int(product["quantity"])
        shop_price = int(float(product["price"]) * 100)
        total_price = shop_price * quantity
        discount = total_price * (discount_percentage / 100)
        to_pay = int(total_price - discount)
        purchase = models.StockPurchase(
            user=user,
            to_pay=to_pay,
            created_by=self.request.user,
            product_id="SHOP PURCHASE",
            product_sku="SHOP PURCHASE",
            product_name=product["name"],
            full_price=shop_price,
            quantity=quantity,
            discount_percentage=discount_percentage,
        )
        purchase.save()


@method_decorator(csrf_exempt, name="dispatch")
class ProductSearch(PurchaseCreatorUserMixin, View):
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
class ProductPurchasePrice(PurchaseCreatorUserMixin, View):
    """View for product purchase price requests."""

    def get(self, *args, **kwargs):
        """Process HTTP request."""
        product_id = self.request.GET.get("product_id")
        product_options = CCAPI.get_options_for_product(product_id)
        purchase_price = product_options["Purchase Price"].value.value
        data = {"product_id": product_id, "purchase_price": purchase_price}
        return JsonResponse(data, safe=False)


@method_decorator(csrf_exempt, name="dispatch")
class MarkOrderCancelled(PurchaseManagerUserMixin, View):
    """Mark a purchase as cancelled."""

    def post(self, *args, **kwargs):
        """Mark a purchase as cancelled."""
        purchase_id = self.request.POST.get("purchase_id")
        purchase = get_object_or_404(models.Purchase, pk=purchase_id)
        purchase.cancelled = True
        purchase.save()
        return JsonResponse({purchase_id: "ok"})


class PurchaseShipping(PurchaseCreatorUserMixin, FormView):
    """View for creating stock purchases."""

    form_class = forms.PurchaseShipping
    template_name = "purchases/shipping.html"

    def form_valid(self, form):
        """Handle completed form."""
        purchase = models.ShippingPurchase(
            user=form.cleaned_data["purchaser"],
            to_pay=form.cleaned_data["price"],
            created_by=self.request.user,
            shipping_price=form.cleaned_data["shipping_price"],
        )
        purchase.save()
        return super().form_valid(form)

    def get_success_url(self):
        """Return the sucess url."""
        return reverse("purchases:manage_purchases")


class PurchaseNote(PurchaserUserMixin, FormView):
    """View for creating purchase notes."""

    form_class = forms.PurchaseNote
    template_name = "purchases/purchase_note.html"

    def form_valid(self, form):
        """Add purchase note to the database."""
        purchase = models.PurchaseNote(
            user=self.request.user,
            to_pay=int(form.cleaned_data["to_pay"] * 100),
            created_by=self.request.user,
            text=form.cleaned_data["text"],
        )
        purchase.save()
        return super().form_valid(form)

    def get_success_url(self):
        """Return the sucess url."""
        messages.success(self.request, "Note added.")
        return reverse("purchases:purchase")


@method_decorator(csrf_exempt, name="dispatch")
class GetShippingPrice(PurchaseCreatorUserMixin, View):
    """Get the shipping price for a given service and weight."""

    def post(self, *args, **kwargs):
        """Get the shipping price for a given service and weight."""
        country = self.request.POST["country"]
        shipping_service = self.request.POST["shipping_service"]
        weight = int(self.request.POST["weight"])
        shipping_price = ShippingPrice.objects.get(
            country=country, shipping_service=shipping_service, inactive=False
        )
        to_pay = shipping_price.price(weight)
        return JsonResponse({"price": to_pay})
