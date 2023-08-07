from io import StringIO

import pytest

from purchases.models import PurchaseExportReport


@pytest.fixture
def export(purchase_export_factory):
    return purchase_export_factory.create()


@pytest.fixture
def staff(staff_factory):
    return staff_factory.create_batch(3)


@pytest.fixture
def staff_purchases(staff, export, purchase_factory):
    return {
        staff_member: purchase_factory.create_batch(
            3, purchased_by=staff_member, export=export
        )
        for staff_member in staff
    }


def test_header():
    assert PurchaseExportReport.header == [
        "Purchased By",
        "SKU",
        "Product",
        "Quantity",
        "Date",
        "Item Price",
        "To Pay",
    ]


@pytest.mark.django_db
def test_get_purchase_row(purchase_factory):
    purchase = purchase_factory.create()
    data = PurchaseExportReport._get_purchase_row(purchase)
    assert data == [
        str(purchase.purchased_by),
        purchase.product.sku,
        purchase.product.full_name,
        purchase.quantity,
        str(purchase.created_at.date()),
        str(purchase.time_of_purchase_item_price),
        str(purchase.to_pay()),
    ]


@pytest.mark.django_db
def test_export_data(staff, staff_purchases):
    data = PurchaseExportReport._get_report_data(staff_purchases)
    assert data == [
        PurchaseExportReport.header,
        PurchaseExportReport._get_purchase_row(staff_purchases[staff[0]][0]),
        PurchaseExportReport._get_purchase_row(staff_purchases[staff[0]][1]),
        PurchaseExportReport._get_purchase_row(staff_purchases[staff[0]][2]),
        [
            "",
            "",
            "",
            "",
            "",
            "",
            str(sum((_.to_pay() for _ in staff_purchases[staff[0]]))),
        ],
        [],
        PurchaseExportReport._get_purchase_row(staff_purchases[staff[1]][0]),
        PurchaseExportReport._get_purchase_row(staff_purchases[staff[1]][1]),
        PurchaseExportReport._get_purchase_row(staff_purchases[staff[1]][2]),
        [
            "",
            "",
            "",
            "",
            "",
            "",
            str(sum((_.to_pay() for _ in staff_purchases[staff[1]]))),
        ],
        [],
        PurchaseExportReport._get_purchase_row(staff_purchases[staff[2]][0]),
        PurchaseExportReport._get_purchase_row(staff_purchases[staff[2]][1]),
        PurchaseExportReport._get_purchase_row(staff_purchases[staff[2]][2]),
        [
            "",
            "",
            "",
            "",
            "",
            "",
            str(sum((_.to_pay() for _ in staff_purchases[staff[2]]))),
        ],
        [],
    ]


@pytest.mark.django_db
def test_generate_report_text_returns_string_io(export):
    assert isinstance(PurchaseExportReport().generate_report_text(export), StringIO)


@pytest.mark.django_db
def test_report_starts_with_header(export):
    expected = ",".join(PurchaseExportReport.header)
    text = PurchaseExportReport().generate_report_text(export).getvalue()
    assert text.startswith(expected)