"""Tests for CartService - demonstrates the bugs."""
import pytest
import sys
sys.path.insert(0, "src")

from checkout.cart_service import CartService


class TestCartService:
    def setup_method(self):
        self.service = CartService()

    def test_add_item_creates_duplicate(self):
        """BUG: Adding same item twice creates duplicates."""
        item = {"item_id": "ITEM-1", "name": "Widget", "price": 9.99, "quantity": 1}
        self.service.add_item("C-1", item)
        self.service.add_item("C-1", item)
        # BUG: Cart has 2 entries instead of quantity=2
        assert len(self.service.carts["C-1"]) == 2

    def test_calculate_total_string_price_fails(self):
        """BUG: Fails when price is string from API."""
        self.service.carts["C-1"] = [
            {"item_id": "ITEM-1", "price": "19.99", "quantity": 2}
        ]
        with pytest.raises(TypeError):
            self.service.calculate_cart_total("C-1")

    def test_checkout_no_inventory_check(self):
        """BUG: Checkout succeeds even if inventory is empty."""
        self.service.carts["C-1"] = [
            {"item_id": "ITEM-1", "price": 10.0, "quantity": 100}
        ]
        # This should fail if inventory only has 5 units
        result = self.service.checkout("C-1")
        assert result["status"] == "confirmed"  # BUG: should check inventory

    def test_remove_item(self):
        self.service.carts["C-1"] = [
            {"item_id": "ITEM-1", "price": 10.0, "quantity": 1},
            {"item_id": "ITEM-2", "price": 20.0, "quantity": 1},
        ]
        result = self.service.remove_item("C-1", "ITEM-1")
        assert result["cart_size"] == 1

    def test_empty_cart_checkout_error(self):
        result = self.service.checkout("C-999")
        assert result["status"] == "error"
