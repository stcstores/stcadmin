"""Tool for calculating FBA profit margins."""


class FBAPriceCalculator:
    """Tool for calculating FBA profit margins."""

    CHANNEL_FEE = 0.15

    def __init__(
        self,
        selling_price,
        region,
        purchase_price,
        fba_fee,
        product_weight,
        stock_level,
        zero_rated,
        quantity,
    ):
        """
        Price calculator for FBA orders.

        Kwargs:
            selling_price (float): The price for which the item will be sold.
            region (fba.models.FBARegion): The region to which the item will be shipped.
            purchase_price (int): The purchase price of the item.
            fba_fee (float): The fee charged by Amazon.
            product_weight (int): The weight of the item in grams.
            stock_level (int): The current stock level of the item.
            zero_rated (bool): True if the item if VAT free, otherwise False.
            quantity (int): The number of items to be sent.
        """
        self.selling_price = selling_price
        self.region = region
        self.purchase_price = purchase_price
        self.fba_fee = fba_fee
        self.product_weight = product_weight
        self.stock_level = stock_level
        self.zero_rated = zero_rated
        self.quantity = quantity

    def to_dict(self):
        """Return FBA profit margin calculations."""
        return {
            "channel_fee": round(self.channel_fee, 2),
            "currency_symbol": self.region.country.currency.symbol,
            "vat": round(self.vat, 2),
            "postage_to_fba": round(self.postage_gbp, 2),
            "postage_per_item": round(self.postage_per_item_gbp, 2),
            "profit": round(self.profit_gbp, 2),
            "percentage": round(self.percentage, 2),
            "purchase_price": round(self.purchase_price_local, 2),
            "max_quantity": self.max_quantity,
            "max_quantity_no_stock": self.max_quantity_no_stock,
        }

    def calculate(self):
        """Get request parameters from POST."""
        self.exchange_rate = float(self.region.country.currency.exchange_rate())
        self.max_quantity, self.max_quantity_no_stock = self.get_max_quantity(
            region=self.region,
            product_weight=self.product_weight,
            stock_level=self.stock_level,
        )
        self.postage_gbp = self.get_postage_to_fba(
            region=self.region,
            product_weight=self.product_weight,
            quantity=self.quantity,
        )
        self.postage_local = self.postage_gbp / self.exchange_rate
        self.vat = self.get_vat(
            region=self.region,
            selling_price=self.selling_price,
            zero_rated=self.zero_rated,
        )
        self.channel_fee = self.selling_price * self.CHANNEL_FEE
        self.purchase_price_local = self.purchase_price / self.exchange_rate
        self.postage_per_item_gbp = self.postage_gbp / int(self.quantity)
        self.postage_per_item_local = self.postage_per_item_gbp / self.exchange_rate
        self.profit = self.calculate_profit(
            selling_price=self.selling_price,
            postage_per_item_local=self.postage_per_item_local,
            channel_fee=self.channel_fee,
            vat=self.vat,
            purchase_price_local=self.purchase_price_local,
            fba_fee=self.fba_fee,
        )
        self.profit_gbp = self.profit * self.exchange_rate
        self.percentage = (self.profit / self.selling_price) * 100

    @staticmethod
    def get_vat(region, zero_rated, selling_price):
        """Return the caclulated VAT."""
        if (
            region.country.vat_is_required() == region.country.VAT_NEVER
            or zero_rated is True
        ):
            return 0.0
        return selling_price / 6

    @staticmethod
    def get_postage_to_fba(region, product_weight, quantity):
        """Return the caclulated price to post to FBA."""
        shipped_weight = product_weight * quantity
        return float(region.calculate_shipping(shipped_weight)) / 100.0

    @staticmethod
    def calculate_profit(
        selling_price,
        postage_per_item_local,
        channel_fee,
        vat,
        purchase_price_local,
        fba_fee,
    ):
        """Return the calculated per item profit."""
        costs = sum(
            (
                postage_per_item_local,
                channel_fee,
                vat,
                purchase_price_local,
                fba_fee,
            )
        )
        return selling_price - costs

    @staticmethod
    def get_max_quantity(region, product_weight, stock_level):
        """Return the maximum number of the product that can be sent."""
        max_quantity = (region.max_weight * 1000) // product_weight
        return min((max_quantity, stock_level)), max_quantity
