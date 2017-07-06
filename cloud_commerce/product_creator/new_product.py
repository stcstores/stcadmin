from ccapi import CCAPI


class NewProduct:

    def __init__(self, data):
        self.load_from_from_data(data)
        self.get_options()
        self.product_range = self.create_range()
        self.products = self.get_products()
        for product in self.products:
            product.create()

    @staticmethod
    def get_bay_id(bay_name, department):
        warehouses = CCAPI.get_warehouses()
        warehouse = warehouses[department]
        if bay_name in warehouse.bay_names:
            return warehouse[bay_name].id
        bay_id = warehouse.add_bay(bay_name)
        return bay_id
