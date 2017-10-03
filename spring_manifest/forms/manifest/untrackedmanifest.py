from . springmanifest import SpringManifest


class UnTrackedManifest(SpringManifest):

    spreadsheet_header = [
        'CustomerNumber', 'Customer Reference 1', 'Customer Reference 2',
        'PO Number', 'Quote Reference', 'Count items', 'Pre-franked',
        'Product Code', 'Nr satchels', 'Nr bags', 'Nr boxes', 'Nr pallets',
        'Destination code', 'Format code', 'Weightbreak from',
        'Weightbreak to', 'Nr items', 'Weight']

    write_header = [
        'CustomerNumber*', 'Customer Reference 1', 'Customer Reference 2',
        'PO Number', 'Quote Reference', 'Count items*', 'Pre-franked*',
        'Product Code*', 'Nr satchels', 'Nr bags', 'Nr boxes', 'Nr pallets',
        'Destination code*', 'Format code', 'Weightbreak from',
        'Weightbreak to', 'Nr items*', 'Weight (kg)*']

    def __init__(self, form, orders):
        self.form = form
        self.orders = orders
        self.manifest()

    def get_rows_for_order(self, order):
        rows = []
        for product in order.products:
            data = {
                'CustomerNumber': self.shipper_id,
                'Customer Reference 1': '',
                'Customer Reference 2': '',
                'PO Number': '',
                'Quote Reference': '',
                'Count items': '',
                'Pre-franked': '',
                'Product Code': '',
                'Nr satchels': '',
                'Nr bags': '',
                'Nr boxes': '',
                'Nr pallets': '',
                'Destination code': '',
                'Format code': '',
                'Weightbreak from': '',
                'Weightbreak to': '',
                'Nr items': '',
                'Weight': '',
            }
            rows.append([data[key] for key in self.spreadsheet_header])
        return rows
