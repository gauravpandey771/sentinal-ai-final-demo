"""Tests for OrderProcessor - demonstrates the bugs."""
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
        assert result["item_count"] == 2

    def test_calculate_total_none_items_crashes(self):
        """BUG: Crashes when items is None."""
        order = {"order_id": "ORD-002", "items": None}
        with pytest.raises(TypeError):
            self.processor.calculate_order_total(order)

    def test_integer_division_truncates_price(self):
        """BUG: Integer division loses decimal precision."""
        order = {
            "order_id": "ORD-003",
            "items": [{"price": 19.99, "quantity": 1}]
        }
        result = self.processor.calculate_order_total(order)
        # Should be 19.99 but integer division gives 19.0
        assert result["subtotal"] == 19.0  # BUG: should be 19.99

    def test_get_status_missing_fulfillment_crashes(self):
        """BUG: Crashes when fulfillment key missing."""
        order = {"order_id": "ORD-004"}
        with pytest.raises(KeyError):
            self.processor.get_order_status(order)

    def test_validate_does_not_catch_none_items(self):
        """BUG: validate_order passes but calculate crashes."""
        order = {"order_id": "ORD-005", "customer_id": "C-1", "items": None}
        errors = self.processor.validate_order(order)
        assert errors == []  # Validation passes incorrectly
