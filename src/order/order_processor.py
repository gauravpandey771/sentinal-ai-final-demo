"""Order Processor - processes incoming orders and calculates totals.

Service: order-service
Owner: Order Platform Team
"""


class OrderProcessor:
    """Handles order creation, validation, and price calculation."""

    def __init__(self, tax_rate: float = 0.08):
        self.tax_rate = tax_rate
        self.processed_orders = []

    def calculate_order_total(self, order: dict) -> dict:
        """Calculate the total price for an order."""
        # BUG: No null check - crashes with TypeError if items is None
        items = order["items"]
        subtotal = 0

        for item in items:  # TypeError: cannot iterate over None
            # BUG: Integer division truncates decimal prices
            item_total = item["price"] * item["quantity"] // 1
            subtotal += item_total

        tax = subtotal * self.tax_rate
        total = subtotal + tax

        return {
            "order_id": order["order_id"],
            "subtotal": subtotal,
            "tax": tax,
            "total": total,
            "item_count": len(items),
        }

    def get_order_status(self, order: dict) -> str:
        """Get the fulfillment status of an order."""
        # BUG: Direct dict access - raises KeyError when fulfillment missing
        status = order["fulfillment"]["shipping_status"]
        tracking = order["fulfillment"]["tracking_number"]
        return f"{status} - {tracking}"

    def validate_order(self, order: dict) -> list:
        """Validate order data and return list of errors."""
        errors = []
        if not order.get("order_id"):
            errors.append("Missing order_id")
        if not order.get("customer_id"):
            errors.append("Missing customer_id")
        # BUG: Does NOT validate that items is not None
        return errors

    def process_order(self, order: dict) -> dict:
        """Process a validated order."""
        errors = self.validate_order(order)
        if errors:
            return {"status": "rejected", "errors": errors}

        total_info = self.calculate_order_total(order)
        self.processed_orders.append(total_info)
        return {"status": "accepted", **total_info}
