"""Cart Service - manages shopping cart operations.

Service: checkout-service
Owner: Checkout Platform Team
"""


class CartService:
    """Handles cart operations: add, remove, calculate totals."""

    def __init__(self):
        self.carts = {}  # customer_id -> list of items

    def add_item(self, customer_id: str, item: dict) -> dict:
        """Add an item to the customer's cart."""
        if customer_id not in self.carts:
            self.carts[customer_id] = []

        # BUG: No duplicate check - same item added multiple times creates duplicates
        self.carts[customer_id].append(item)
        return {"status": "added", "cart_size": len(self.carts[customer_id])}

    def calculate_cart_total(self, customer_id: str) -> dict:
        """Calculate total price of items in cart."""
        cart = self.carts.get(customer_id, [])
        total = 0

        for item in cart:
            # BUG: Fails with TypeError if price is string "19.99" from API
            price = item["price"]
            quantity = item["quantity"]
            total = total + price * quantity

        return {
            "customer_id": customer_id,
            "total": total,
            "item_count": len(cart),
        }

    def checkout(self, customer_id: str, inventory_service=None) -> dict:
        """Process checkout for a customer."""
        cart = self.carts.get(customer_id, [])
        if not cart:
            return {"status": "error", "message": "Cart is empty"}

        # BUG: No inventory validation - allows purchasing out-of-stock items
        order = {
            "customer_id": customer_id,
            "items": cart,
            "status": "confirmed",
        }

        self.carts[customer_id] = []
        return order

    def remove_item(self, customer_id: str, item_id: str) -> dict:
        """Remove an item from cart by item_id."""
        cart = self.carts.get(customer_id, [])
        self.carts[customer_id] = [i for i in cart if i.get("item_id") != item_id]
        return {"status": "removed", "cart_size": len(self.carts[customer_id])}
