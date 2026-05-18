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

        # FIX: Check for duplicates - increment quantity if item exists
        for existing in self.carts[customer_id]:
            if existing.get("item_id") == item.get("item_id"):
                existing["quantity"] = existing.get("quantity", 1) + item.get("quantity", 1)
                return {"status": "updated", "cart_size": len(self.carts[customer_id])}

        self.carts[customer_id].append(item)
        return {"status": "added", "cart_size": len(self.carts[customer_id])}

    def calculate_cart_total(self, customer_id: str) -> dict:
        """Calculate total price of items in cart."""
        cart = self.carts.get(customer_id, [])
        total = 0.0

        for item in cart:
            # FIX: Ensure price is numeric - convert strings to float
            price = float(item.get("price", 0))
            quantity = int(item.get("quantity", 0))
            total += price * quantity

        return {
            "customer_id": customer_id,
            "total": round(total, 2),
            "item_count": len(cart),
        }

    def checkout(self, customer_id: str, inventory_service=None) -> dict:
        """Process checkout for a customer."""
        cart = self.carts.get(customer_id, [])
        if not cart:
            return {"status": "error", "message": "Cart is empty"}

        # FIX: Validate inventory before checkout
        if inventory_service:
            for item in cart:
                available = inventory_service.check_stock(item.get("item_id"), item.get("quantity", 1))
                if not available:
                    return {
                        "status": "error",
                        "message": f"Item {item.get('item_id')} is out of stock",
                    }

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
