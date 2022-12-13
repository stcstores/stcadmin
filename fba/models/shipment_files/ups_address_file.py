"""UPS Address file generator."""

import csv
import io


class UPSAddressFile:
    """UPS Address file generator."""

    COMPANY_NAME = "CompanyName"
    ATTENTION = "Attention"
    SHIP_TO_ADDRESS_1 = "ShiptoAddress1"
    SHIP_TO_ADDRESS_3 = "ShiptoAddress3"
    SHIP_CITY = "ShipCity"
    SHIP_TO_STATE = "ShiptoState"
    SHIP_TO_COUNTRY = "ShiptoCountry"
    SHIP_TO_POSTCODE = "ShiptoPostcode"
    SHIP_TO_PHONE = "ShipToPhone"
    SHIP_TO_EMAIL = "ShiptoEmail"
    GNERAL_DESCRIPTION = "GneralDescription"
    BILL_TRANSPORT_TO = "BillTransportTo"
    BILL_DUTY_AND_TAX = "BillDutyandTax"
    NUMBER_OF_PACKAGES = "NumberofPackag"
    ACTUAL_WEIGHT = "ActualWeight"
    PACKAGE_TYPE = "PackageType"
    SERVICETYPE = "ServiceType"
    ORDER_NUMBER = "OrderNumber"
    CURRENCY_CODE = "CurrencyCode"
    RATECARD_REFERENCE = "RatecardReference"

    HEADER = [
        COMPANY_NAME,
        ATTENTION,
        SHIP_TO_ADDRESS_1,
        SHIP_TO_ADDRESS_3,
        SHIP_CITY,
        SHIP_TO_STATE,
        SHIP_TO_COUNTRY,
        SHIP_TO_POSTCODE,
        SHIP_TO_PHONE,
        SHIP_TO_EMAIL,
        GNERAL_DESCRIPTION,
        BILL_TRANSPORT_TO,
        BILL_DUTY_AND_TAX,
        NUMBER_OF_PACKAGES,
        ACTUAL_WEIGHT,
        PACKAGE_TYPE,
        SERVICETYPE,
        ORDER_NUMBER,
        CURRENCY_CODE,
        RATECARD_REFERENCE,
    ]

    @classmethod
    def _create_rows(cls, shipment_export):
        shipments = shipment_export.shipment_order.all()
        rows = [cls._create_address_row(shipment) for shipment in shipments]
        return rows

    @classmethod
    def _create_address_row(cls, shipment):
        destination = shipment.destination
        row_data = {
            cls.COMPANY_NAME: destination.recipient_name,
            cls.ATTENTION: destination.address_line_1,
            cls.SHIP_TO_ADDRESS_1: destination.address_line_2,
            cls.SHIP_TO_ADDRESS_3: destination.address_line_3,
            cls.SHIP_CITY: destination.city,
            cls.SHIP_TO_STATE: destination.state,
            cls.SHIP_TO_COUNTRY: destination.country,
            cls.SHIP_TO_POSTCODE: destination.postcode,
            cls.SHIP_TO_EMAIL: "test@amazon.com",
            cls.GNERAL_DESCRIPTION: "TEST",
            cls.BILL_TRANSPORT_TO: "SHP",
            cls.BILL_DUTY_AND_TAX: "REC",
            cls.NUMBER_OF_PACKAGES: shipment.shipment_package.count(),
            cls.ACTUAL_WEIGHT: shipment.weight_kg(),
            cls.PACKAGE_TYPE: "SV",
            cls.ORDER_NUMBER: shipment.order_number(),
            cls.CURRENCY_CODE: "GBP",
            cls.RATECARD_REFERENCE: "WI-STC001",
        }
        return [row_data.get(col) for col in cls.HEADER]

    @classmethod
    def create(cls, shipment_export):
        """Generate a shipment file for the orders associated with an export."""
        rows = cls._create_rows(shipment_export)
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(cls.HEADER)
        for row in rows:
            writer.writerow(row)
        return output.getvalue()
