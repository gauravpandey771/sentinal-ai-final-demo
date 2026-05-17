"""Tests for PaymentGatewayClient - verifies fixes for timeout, null-safety, and retry."""
import pytest
from unittest.mock import patch, MagicMock
import sys
sys.path.insert(0, "src")

from payment.gateway_client import PaymentGatewayClient, MAX_RETRIES


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

    def test_process_response_null_transaction_handled(self):
        """FIX: Returns error dict instead of crashing."""
        response = {"transaction": None}
        result = self.client.process_payment_response(response)
        assert result["status"] == "error"
        assert result["error"] is not None

    def test_process_response_missing_field_handled(self):
        """FIX: Missing fields default to None/0."""
        response = {"transaction": {"id": "TXN-002", "status": "ok"}}
        result = self.client.process_payment_response(response)
        assert result["transaction_id"] == "TXN-002"
        assert result["auth_code"] is None
        assert result["amount_charged"] == 0

    def test_retry_respects_max_attempts(self):
        """FIX: Retry stops after MAX_RETRIES attempts."""
        with patch.object(self.client, "authorize_payment", side_effect=Exception("timeout")):
            with pytest.raises(RuntimeError, match=f"after {MAX_RETRIES} attempts"):
                self.client.authorize_with_retry("ORD-1", 100.0)

    def test_refund_valid(self):
        result = self.client.refund_payment("TXN-001", 50.0)
        assert result["status"] == "processed"

    def test_refund_negative_amount(self):
        with pytest.raises(ValueError):
            self.client.refund_payment("TXN-001", -10.0)
