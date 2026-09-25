import uuid
from decimal import Decimal


def process_mock_payment(amount: Decimal, user_id: int, payment_token: str = "mock_token_ok") -> str:
    """Mock payment gateway stub that simulates successful charge processing."""
    if payment_token == "mock_token_fail":
        raise ValueError("Payment processing failed: Invalid card or insufficient funds.")
    payment_ref = f"pay_ref_{uuid.uuid4().hex[:12]}"
    print(f"[MOCK PAYMENT] Processed charge of ${amount} for User ID {user_id}. Ref: {payment_ref}")
    return payment_ref


def process_mock_refund(payment_ref: str, amount: Decimal = None):
    """Mock refund gateway callback triggered if checkout transaction rolls back post-payment."""
    print(f"[MOCK REFUND] Refunded payment reference {payment_ref}. Amount: {amount if amount else 'FULL'}")
