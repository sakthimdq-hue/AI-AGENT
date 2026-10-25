"""
Payment Processor Module (Has a bug for demoing autonomous agent fix)
"""

class PaymentProcessor:
    def __init__(self, currency: str = "USD"):
        self.currency = currency

    def calculate_total(self, subtotal: float, discount_percent: float, tax_percent: float) -> float:
        """
        Calculate total after applying discount first, then adding tax.
        
        BUG: The developer accidentally added the discount instead of subtracting it,
        and applied tax to the raw subtotal!
        """
        # BUG HERE:
        discounted_amount = subtotal + (subtotal * (discount_percent / 100))
        tax_amount = subtotal * (tax_percent / 100)
        return round(discounted_amount + tax_amount, 2)

    def process_refund(self, amount: float, fee_percent: float = 2.0) -> float:
        """Calculate refundable amount after deducting processing fee."""
        if amount <= 0:
            raise ValueError("Amount must be greater than zero")
        fee = amount * (fee_percent / 100)
        return round(amount - fee, 2)
