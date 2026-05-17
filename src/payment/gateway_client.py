"""Payment Gateway Client - handles authorization calls to payment provider.

Service: payment-service
Owner: Payments Platform Team
"""
import json
import urllib.request
import time

MAX_RETRIES = 3
TIMEOUT_MS = 750


class PaymentGatewayClient:
    """Client for external payment gateway communication."""

    def __init__(self, base_url: str = "https://gateway.payments.internal"):
        self.base_url = base_url

    def authorize_payment(self, order_id: str, amount: float, currency: str = "USD") -> dict:
        """Send authorization request to payment gateway."""
        payload = json.dumps({
            "order_id": order_id,
            "amount": amount,
            "currency": currency,
        }).encode("utf-8")

        req = urllib.request.Request(
            f"{self.base_url}/v1/authorize",
            data=payload,
            headers={"Content-Type": "application/json"},
        )
        # FIX: Added timeout to prevent indefinite blocking
        resp = urllib.request.urlopen(req, timeout=TIMEOUT_MS / 1000)
        return json.loads(resp.read().decode())

    def process_payment_response(self, response: dict) -> dict:
        """Extract payment details from gateway response."""
        # FIX: Added null-safety checks for nested fields
        transaction = response.get("transaction")
        if not transaction or not isinstance(transaction, dict):
            return {
                "transaction_id": None,
                "status": "error",
                "auth_code": None,
                "amount_charged": 0,
                "receipt": None,
                "error": "Invalid or missing transaction in response",
            }

        transaction_id = transaction.get("id")
        status = transaction.get("status", "unknown")
        auth_code = transaction.get("auth_code")
        amount = transaction.get("amount", 0)

        return {
            "transaction_id": transaction_id,
            "status": status,
            "auth_code": auth_code,
            "amount_charged": amount,
            "receipt": f"RCP-{transaction_id}" if transaction_id else None,
        }

    def authorize_with_retry(self, order_id: str, amount: float, currency: str = "USD") -> dict:
        """Retry authorization with bounded retries and exponential backoff."""
        # FIX: Added max retries, exponential backoff, and proper error propagation
        last_error = None
        for attempt in range(MAX_RETRIES):
            try:
                return self.authorize_payment(order_id, amount, currency)
            except Exception as e:
                last_error = e
                backoff = 0.1 * (2 ** attempt)  # Exponential backoff
                time.sleep(backoff)
        raise RuntimeError(
            f"Payment authorization failed after {MAX_RETRIES} attempts: {last_error}"
        )

    def refund_payment(self, transaction_id: str, amount: float) -> dict:
        """Process a refund for a given transaction."""
        if amount <= 0:
            raise ValueError("Refund amount must be positive")
        return {
            "refund_id": f"REF-{transaction_id}",
            "status": "processed",
            "amount": amount,
        }
