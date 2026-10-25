"""
Unit tests for PaymentProcessor.
Currently fails because of the calculation bug in payment_processor.py!
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from payment_processor import PaymentProcessor

class TestPaymentProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = PaymentProcessor()

    def test_calculate_total_standard(self):
        # Subtotal: $100, Discount: 10% ($10 off -> $90), Tax: 10% on $90 ($9 tax) -> Total: $99.00
        # With bug: 100 + 10 = 110, tax = 10 -> 120.00 (FAILS!)
        total = self.processor.calculate_total(subtotal=100.0, discount_percent=10.0, tax_percent=10.0)
        self.assertEqual(total, 99.00)

    def test_calculate_total_zero_discount(self):
        total = self.processor.calculate_total(subtotal=50.0, discount_percent=0.0, tax_percent=8.0)
        self.assertEqual(total, 54.00)

    def test_refund_standard(self):
        refund = self.processor.process_refund(amount=100.0, fee_percent=2.5)
        self.assertEqual(refund, 97.50)

    def test_refund_negative_amount_raises(self):
        with self.assertRaises(ValueError):
            self.processor.process_refund(amount=-10.0)

if __name__ == '__main__':
    unittest.main()
