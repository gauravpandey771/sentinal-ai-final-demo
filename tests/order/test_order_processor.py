"""Tests for OrderProcessor - verifies null-safety and precision fixes."""
import pytest
import sys
sys.path.insert(0, "src")

from order.order_processor import OrderProcessor


class TestOrderProcessor:
    def setup_method(self):
        self.processor = OrderProcessor(tax_rate=0.08)

    def test_calculate_total_valid_order(self):
        order = {
            "order_id": "ORD-001",
            "items": [
                {"price": 10.0, "quantity": 2},
                {"price": 5.0, "quantity": 1},
            ]
        }
        result = self.processor.calculate_order_total(order)
        assert result["order_id"] == "ORD-001"
        assert result["subtotal"] == 25.0
        assert result["item_count"] == 2

    def test_calculate_total_none_items_returns_zero(self):
        """FIX: None items returns zero totals instead of crashing."""
        order = {"order_id": "ORD-002", "items": None}
        result = self.processor.calculate_order_total(order)
        assert result["subtotal"] == 0.0
        assert result["item_count"] == 0

    def test_float_precision_preserved(self):
        """FIX: Float multiplication preserves decimal precision."""
        order = {
            "order_id": "ORD-003",
            "items": [{"price": 19.99, "quantity": 1}]
        }
        result = self.processor.calculate_order_total(order)
        assert result["subtotal"] == 19.99

    def test_get_status_missing_fulfillment_safe(self):
        """FIX: Returns defaults instead of crashing."""
        order = {"order_id": "ORD-004"}
        result = self.processor.get_order_status(order)
        assert "unknown" in result

    def test_validate_catches_none_items(self):
        """FIX: Validation now catches None items."""
        order = {"order_id": "ORD-005", "customer_id": "C-1", "items": None}
        errors = self.processor.validate_order(order)
        assert "Items cannot be None" in errors
