"""Tests for CartService - verifies duplicate, type-safety, and inventory fixes."""
import pytest
import sys
sys.path.insert(0, "src")

from checkout.cart_service import CartService


class TestCartService:
    def setup_method(self):
        self.service = CartService()

    def test_add_item_deduplicates(self):
        """FIX: Adding same item increments quantity."""
        item = {"item_id": "ITEM-1", "name": "Widget", "price": 9.99, "quantity": 1}
        self.service.add_item("C-1", item)
        result = self.service.add_item("C-1", item.copy())
        assert result["status"] == "updated"
        assert len(self.service.carts["C-1"]) == 1
        assert self.service.carts["C-1"][0]["quantity"] == 2

    def test_calculate_total_string_price_handled(self):
        """FIX: String prices are converted to float."""
        self.service.carts["C-1"] = [
            {"item_id": "ITEM-1", "price": "19.99", "quantity": 2}
        ]
        result = self.service.calculate_cart_total("C-1")
        assert result["total"] == 39.98

    def test_checkout_with_inventory_check(self):
        """FIX: Checkout validates inventory when service provided."""
        class MockInventory:
            def check_stock(self, item_id, qty):
                return False  # Out of stock

        self.service.carts["C-1"] = [
            {"item_id": "ITEM-1", "price": 10.0, "quantity": 100}
        ]
        result = self.service.checkout("C-1", inventory_service=MockInventory())
        assert result["status"] == "error"
        assert "out of stock" in result["message"]

    def test_checkout_without_inventory_still_works(self):
        """Backwards compatible - checkout works without inventory service."""
        self.service.carts["C-1"] = [
            {"item_id": "ITEM-1", "price": 10.0, "quantity": 1}
        ]
        result = self.service.checkout("C-1")
        assert result["status"] == "confirmed"

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
