"""UPS Address file generator."""

import csv
import io


class UPSAddressFile:
    """UPS Address file generator."""

    COMPANYNAME = "CompanyName"
    ATTENTION = "Attention"
    SHIPTOADDRESS1 = "ShiptoAddress1"
    SHIPTOADDRESS3 = "ShiptoAddress3"
    SHIPCITY = "ShipCity"
    SHIPTOSTATE = "ShiptoState"
    SHIPTOCOUNTRY = "ShiptoCountry"
    SHIPTOPOSTCODE = "ShiptoPostcode"
    SHIPTOPHONE = "ShipToPhone"
    SHIPTOEMAIL = "ShiptoEmail"
    GNERALDESCRIPTION = "GneralDescription"
    BILLTRANSPORTTO = "BillTransportTo"
    BILLDUTYANDTAX = "BillDutyandTax"
    NUMBEROFPACKAG = "NumberofPackag"
    ACTUALWEIGHT = "ActualWeight"
    PACKAGETYPE = "PackageType"
    SERVICETYPE = "ServiceType"
    ORDERNUMBER = "OrderNumber"
    CURRENCYCODE = "CurrencyCode"

    HEADER = [
        COMPANYNAME,
        ATTENTION,
        SHIPTOADDRESS1,
        SHIPTOADDRESS3,
        SHIPCITY,
        SHIPTOSTATE,
        SHIPTOCOUNTRY,
        SHIPTOPOSTCODE,
        SHIPTOPHONE,
        SHIPTOEMAIL,
        GNERALDESCRIPTION,
        BILLTRANSPORTTO,
        BILLDUTYANDTAX,
        NUMBEROFPACKAG,
        ACTUALWEIGHT,
        PACKAGETYPE,
        SERVICETYPE,
        ORDERNUMBER,
        CURRENCYCODE,
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
            cls.COMPANYNAME: destination.recipient_name,
            cls.ATTENTION: destination.address_line_1,
            cls.SHIPTOADDRESS1: destination.address_line_2,
            cls.SHIPTOADDRESS3: destination.address_line_3,
            cls.SHIPCITY: destination.city,
            cls.SHIPTOSTATE: destination.state,
            cls.SHIPTOCOUNTRY: destination.country,
            cls.SHIPTOPOSTCODE: destination.postcode,
            cls.SHIPTOEMAIL: "test@amazon.com",
            cls.GNERALDESCRIPTION: "TEST",
            cls.BILLTRANSPORTTO: "SHP",
            cls.BILLDUTYANDTAX: "REC",
            cls.NUMBEROFPACKAG: shipment.shipment_package.count(),
            cls.ACTUALWEIGHT: shipment.weight_kg(),
            cls.PACKAGETYPE: "SV",
            cls.ORDERNUMBER: shipment.order_number(),
            cls.CURRENCYCODE: "GBP",
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
