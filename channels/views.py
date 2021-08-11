"""Views for the channels app."""

import csv
import json
import traceback
from io import StringIO

from ccapi import CCAPI
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import RedirectView, TemplateView, View
from django.views.generic.edit import FormView
from file_exchange.views import DownloadFileView, FileDownloadStatusView

from channels import forms, models
from home.views import UserInGroupMixin
from shipping.models import Country


class ChannelsUserMixin(UserInGroupMixin):
    """View mixin to ensure user is in the channels group."""

    groups = ["channels"]


class Index(ChannelsUserMixin, TemplateView):
    """Main view for the orders app."""

    template_name = "channels/index.html"


class CreateOrderChannelSelect(ChannelsUserMixin, TemplateView):
    """View for selecting a channel to create an order for."""

    template_name = "channels/create_order_channel_select.html"

    def get_context_data(self, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(**kwargs)
        context["channels"] = models.Channel.active.all()
        return context


class CreateOrder(ChannelsUserMixin, FormView):
    """View for creating orders."""

    form_class = forms.CreateOrder
    template_name = "channels/new_order.html"

    def get_form_kwargs(self):
        """Set form kwargs."""
        kwargs = super().get_form_kwargs()
        kwargs["channel"] = models.Channel.objects.get(pk=self.kwargs.get("channel_pk"))
        return kwargs

    def form_valid(self, form):
        """Create the order."""
        data = form.cleaned_data
        data["channel"] = form.channel.channel_id
        self.order_object = models.CreateOrder(data).create()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(**kwargs)
        context["countries"] = Country.objects.values_list("name", flat=True)
        return context

    def get_success_url(self):
        """Redirect after successful submission."""
        return self.order_object.get_absolute_url()


class ImportOrders(ChannelsUserMixin, TemplateView):
    """View for uploading orders via .csv."""

    template_name = "channels/import_orders.html"


class ImportWishOrders(ChannelsUserMixin, RedirectView):
    """View for importing orders from Wish."""

    COUNTRY_CONVERSION = {"United Kingdom (Great Britain)": "United Kingdom"}

    def get_redirect_url(self, *args, **kwargs):
        """Redirect to the results page."""
        return reverse(
            "channels:wish_import_results", kwargs={"pk": self.import_object.pk}
        )

    def convert_country(self, country_name):
        """Replace a Wish country name with a Cloud Commerce country name."""
        if country_name in self.COUNTRY_CONVERSION:
            return self.COUNTRY_CONVERSION[country_name]
        return country_name

    def post(self, request, *args, **kwargs):
        """Import orders from a Wish template."""
        uploaded_file = request.FILES["wish_file"]
        reader = csv.reader(StringIO(uploaded_file.read().decode("utf8")))
        channel_id = models.Channel.objects.get(name="Telephone Channel").channel_id
        self.import_object = models.WishImport()
        self.import_object.save()
        for row_number, row_data in enumerate(reader):
            if row_number == 0:
                header = row_data
                continue
            row = dict(zip(header, [value for value in row_data]))
            if models.WishOrder.objects.filter(
                wish_order_id=row["Order Id"], order__isnull=False
            ).exists():
                models.WishOrder(
                    wish_import=self.import_object,
                    wish_transaction_id=row["Transaction ID"],
                    wish_order_id=row["Order Id"],
                    error="Already Created",
                ).save()
                continue
            product_id = CCAPI.search_product_SKU(
                row["SKU"],
                channel_id=channel_id,
            )[0].variation_id
            product = {
                "product_id": product_id,
                "price": float(row["Price (each)"][1:]),
                "quantity": int(row["Quantity"]),
            }
            data = {
                "basket": json.dumps([product]),
                "customer_name": row["Name"],
                "address_line_1": row["Street Address 1"],
                "address_line_2": row["Street Address 2"],
                "town": row["City"],
                "post_code": row["Zipcode"],
                "region": row["State"],
                "country": self.convert_country(row["Country"]),
                "channel": channel_id,
                "shipping_price": float(row["Shipping (each)"][1:])
                * product["quantity"],
                "phone_number": row["Phone Number"],
                "email": None,
                "sale_price": None,
            }
            try:
                order = models.CreateOrder(data).create()
            except Exception as e:
                models.WishOrder(
                    wish_import=self.import_object,
                    wish_transaction_id=row["Transaction ID"],
                    wish_order_id=row["Order Id"],
                    error=str(e) + traceback.format_exc(),
                ).save()
            else:
                models.WishOrder(
                    wish_import=self.import_object,
                    wish_transaction_id=row["Transaction ID"],
                    wish_order_id=row["Order Id"],
                    order=order,
                ).save()
        return super().post(request, *args, **kwargs)


class WishImportResults(ChannelsUserMixin, TemplateView):
    """View for wish import results."""

    template_name = "channels/wish_import_result.html"

    def get_context_data(self, **kwargs):
        """Return context for the view."""
        context = super().get_context_data(**kwargs)
        context["wish_import"] = get_object_or_404(
            models.WishImport, pk=self.kwargs["pk"]
        )
        context["orders"] = context["wish_import"].wishorder_set.all()
        return context


class CreatedOrder(ChannelsUserMixin, TemplateView):
    """View for created orders."""

    template_name = "channels/created_order.html"

    def get_context_data(self, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(**kwargs)
        context["order"] = models.CreatedOrder.objects.get(pk=self.kwargs.get("pk"))
        return context


class WishFulfilmentExports(ChannelsUserMixin, DownloadFileView):
    """View for displaying recent Wish Order Fulfilment files."""

    template_name = "channels/wish_fulfilment_exports.html"
    create_file_url = reverse_lazy("channels:create_new_wish_order_fulflment_file")
    status_url = reverse_lazy("channels:wish_order_fulfilment_file_status")

    def get_context_data(self, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(**kwargs)
        context["exports"] = models.WishBulkFulfilmentExport.objects.exclude(
            download_file=""
        ).order_by("-completed_at")[:50]
        return context


class WishFulfilmentExport(ChannelsUserMixin, TemplateView):
    """View for reviewing Wish Order Fulfilment files."""

    template_name = "channels/wish_fulfilment_export.html"

    def get_context_data(self, **kwargs):
        """Return context for the template."""
        context = super().get_context_data(**kwargs)
        export_id = self.kwargs.get("pk")
        object = get_object_or_404(models.WishBulkFulfilmentExport, pk=export_id)
        context["object"] = object
        context["orders"] = object.wishorder_set.select_related("order").all()
        return context


class DownloadWishfulfilmentFile(ChannelsUserMixin, View):
    """View for downloading Wish Order Fulfilment files."""

    def get(self, *args, **kwargs):
        """Return a wish order fulfilment file download."""
        contents = models.WishBulkfulfilFile.get_file()
        response = HttpResponse(contents, content_type="text/csv")
        filename = f"wish_bulk_filfillment_{timezone.now().strftime('%Y-%m-%d')}.csv"
        response["Content-Disposition"] = f"attachment; filename={filename}"
        return response


class CreateNewWishOrderFulfilmentFile(ChannelsUserMixin, View):
    """View for triggering the generation of a new wish order fulfilment file."""

    def get(self, *args, **kwargs):
        """Generate a new wish order fulfilment file."""
        models.WishBulkFulfilmentExport.objects.create_download()
        return HttpResponse("ok")


@method_decorator(csrf_exempt, name="dispatch")
class MarkWishOrderUnfulfiled(ChannelsUserMixin, View):
    """View for marking wish orders as unfulfiled."""

    def post(self, *args, **kwargs):
        """Mark a wish order as unfulfiled."""
        order = get_object_or_404(
            models.WishOrder, pk=self.request.POST.get("order_id")
        )
        order.fulfiled = False
        order.save()
        return HttpResponse("ok")


@method_decorator(csrf_exempt, name="dispatch")
class DelayWishOrderFulfilment(ChannelsUserMixin, View):
    """View for removing wish orders from existing fulfilment file records."""

    def post(self, *args, **kwargs):
        """Mark a wish order unfulfiled and remove it from any fulfilment exports."""
        order = get_object_or_404(
            models.WishOrder, pk=self.request.POST.get("order_id")
        )
        order.fulfiled = False
        order.fulfilment_export = None
        order.save()
        return HttpResponse("ok")


class WishOrderFulfilmentFileStatus(ChannelsUserMixin, FileDownloadStatusView):
    """View for wish order fulfilment file status."""

    model = models.WishBulkFulfilmentExport
