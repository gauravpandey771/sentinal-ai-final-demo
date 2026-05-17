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
        # FIX: Null-safety for items - default to empty list
        items = order.get("items") or []
        subtotal = 0.0

        for item in items:
            # FIX: Use float multiplication instead of integer division
            price = float(item.get("price", 0))
            quantity = int(item.get("quantity", 0))
            item_total = price * quantity
            subtotal += item_total

        tax = round(subtotal * self.tax_rate, 2)
        total = round(subtotal + tax, 2)

        return {
            "order_id": order.get("order_id"),
            "subtotal": subtotal,
            "tax": tax,
            "total": total,
            "item_count": len(items),
        }

    def get_order_status(self, order: dict) -> str:
        """Get the fulfillment status of an order."""
        # FIX: Safe nested access with .get() and defaults
        fulfillment = order.get("fulfillment") or {}
        status = fulfillment.get("shipping_status", "unknown")
        tracking = fulfillment.get("tracking_number", "N/A")
        return f"{status} - {tracking}"

    def validate_order(self, order: dict) -> list:
        """Validate order data and return list of errors."""
        errors = []
        if not order.get("order_id"):
            errors.append("Missing order_id")
        if not order.get("customer_id"):
            errors.append("Missing customer_id")
        # FIX: Validate items is not None and is a list
        items = order.get("items")
        if items is None:
            errors.append("Items cannot be None")
        elif not isinstance(items, list):
            errors.append("Items must be a list")
        return errors

    def process_order(self, order: dict) -> dict:
        """Process a validated order."""
        errors = self.validate_order(order)
        if errors:
            return {"status": "rejected", "errors": errors}

        total_info = self.calculate_order_total(order)
        self.processed_orders.append(total_info)
        return {"status": "accepted", **total_info}
