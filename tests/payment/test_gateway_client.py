"""Tests for PaymentGatewayClient - demonstrates the bugs."""
import pytest
from unittest.mock import patch, MagicMock
import sys
sys.path.insert(0, "src")

from payment.gateway_client import PaymentGatewayClient


class TestPaymentGatewayClient:
    def setup_method(self):
        self.client = PaymentGatewayClient("http://localhost:8080")

    def test_process_response_with_valid_data(self):
        response = {
            "transaction": {
                "id": "TXN-001",
                "status": "authorized",
                "auth_code": "AUTH-123",
                "amount": 99.99,
            }
        }
        result = self.client.process_payment_response(response)
        assert result["transaction_id"] == "TXN-001"
        assert result["status"] == "authorized"

    def test_process_response_null_transaction_crashes(self):
        """BUG: Crashes when transaction is None."""
        response = {"transaction": None}
        with pytest.raises(TypeError):
            self.client.process_payment_response(response)

    def test_process_response_missing_field_crashes(self):
        """BUG: Crashes when auth_code missing."""
        response = {"transaction": {"id": "TXN-002", "status": "ok", "amount": 10.0}}
        with pytest.raises(KeyError):
            self.client.process_payment_response(response)

    def test_refund_valid(self):
        result = self.client.refund_payment("TXN-001", 50.0)
        assert result["status"] == "processed"
        assert result["amount"] == 50.0

    def test_refund_negative_amount(self):
        with pytest.raises(ValueError):
            self.client.refund_payment("TXN-001", -10.0)
