"""Payment Gateway Client - handles authorization calls to payment provider.

Service: payment-service
Owner: Payments Platform Team
"""
import json
import urllib.request
import time


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
        # BUG: No timeout parameter - request blocks indefinitely if gateway unresponsive
        resp = urllib.request.urlopen(req)
        return json.loads(resp.read().decode())

    def process_payment_response(self, response: dict) -> dict:
        """Extract payment details from gateway response."""
        # BUG: Direct nested key access - raises KeyError/TypeError on null response
        transaction_id = response["transaction"]["id"]
        status = response["transaction"]["status"]
        auth_code = response["transaction"]["auth_code"]
        amount = response["transaction"]["amount"]

        return {
            "transaction_id": transaction_id,
            "status": status,
            "auth_code": auth_code,
            "amount_charged": amount,
            "receipt": f"RCP-{transaction_id}",
        }

    def authorize_with_retry(self, order_id: str, amount: float, currency: str = "USD") -> dict:
        """Retry authorization until success."""
        # BUG: Infinite retry loop - no max attempts, no backoff, no circuit breaker
        while True:
            try:
                return self.authorize_payment(order_id, amount, currency)
            except Exception:
                time.sleep(0.1)  # Spins forever on persistent failures

    def refund_payment(self, transaction_id: str, amount: float) -> dict:
        """Process a refund for a given transaction."""
        if amount <= 0:
            raise ValueError("Refund amount must be positive")
        return {
            "refund_id": f"REF-{transaction_id}",
            "status": "processed",
            "amount": amount,
        }
