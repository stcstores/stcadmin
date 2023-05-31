"""Views for the restock app."""

from collections import defaultdict

from django.db.models import Q
from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import TemplateView, View

from home.views import UserInGroupMixin
from inventory.models import BaseProduct


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
        context["suppliers"] = self.get_supplier_products(search_text)
        return context

    def get_supplier_products(self, search_text):
        """Return a dict of {supplier:[products]}."""
        search_terms = [_.strip() for _ in search_text.split()]
        search_terms = [_ for _ in search_terms if _]
        suppliers = defaultdict(list)
        products = (
            BaseProduct.objects.filter(
                Q(sku__in=search_terms) | Q(supplier_sku__in=search_terms)
            )
            .distinct()
            .select_related("supplier")
            .order_by("supplier__name")
        )
        for product in products:
            suppliers[product.supplier].append(product)
        return dict(suppliers)


@method_decorator(csrf_exempt, name="dispatch")
class UpdatePurchasePrice(RestockUserMixin, View):
    """View for handling purchase price updates from the restock page."""

    def post(self, *args, **kwargs):
        """Update purchase price."""
        try:
            self.update_purchase_price()
        except Exception:
            return HttpResponseBadRequest()
        else:
            return HttpResponse(status=200)

    def update_purchase_price(self):
        """Update purchase price."""
        product_id = self.request.POST["product_id"]
        updated_purchase_price = self.request.POST["updated_purchase_price"]
        product = get_object_or_404(BaseProduct, id=product_id)
        product.purchase_price = updated_purchase_price
        product.save()
