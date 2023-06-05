"""Views for the restock app."""

from collections import defaultdict

from django.db.models import Q
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView, View

from home.views import UserInGroupMixin
from inventory.models import BaseProduct
from restock import models


class RestockUserMixin(UserInGroupMixin):
    """Mixin to validate user in in inventory group."""

    groups = ["restock"]


class RestockView(RestockUserMixin, TemplateView):
    """View for the restock page."""

    template_name = "restock/restock.html"


class SearchResults(RestockUserMixin, TemplateView):
    """View for restock page search results."""

    template_name = "restock/restock_results.html"

    def get_context_data(self, *args, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(*args, **kwargs)
        search_text = self.request.GET["product_search"]
        products = self.get_products(search_text)
        context["suppliers"] = self.get_supplier_products(products)
        context["reorder_counts"] = self.get_reorder_counts(products)
        return context

    def get_products(self, search_text):
        """Return products matching the search string."""
        search_terms = [_.strip() for _ in search_text.split()]
        search_terms = [_ for _ in search_terms if _]
        return (
            BaseProduct.objects.filter(
                Q(sku__in=search_terms) | Q(supplier_sku__in=search_terms)
            )
            .distinct()
            .select_related("supplier")
            .order_by("supplier__name")
        )

    def get_supplier_products(self, products):
        """Return a dict of {supplier:[products]}."""
        suppliers = defaultdict(list)
        for product in products:
            suppliers[product.supplier].append(product)
        return dict(suppliers)

    def get_reorder_counts(self, products):
        """Return Reorder objects relating to searched products."""
        reorders = models.Reorder.objects.filter(product__in=products)
        return {reorder.product.id: reorder.count for reorder in reorders}


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
        product.purchase_price = updated_purchase_price
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
