import unittest
from unittest.mock import patch, mock_open
import os
import backend as bls

class TestBankLoanSystem(unittest.TestCase):
    """Comprehensive test suite for the Bank Loan Management System."""

    def tearDown(self):
        """Clean up by removing the created CSV file after tests."""
        if os.path.exists(bls.CSV_FILE):
            os.remove(bls.CSV_FILE)

    # ----------------------------------------
    # 1. Input Validation & Error Handling Tests
    # ----------------------------------------
    @patch('builtins.input', side_effect=['abc', '4', '-1', '2'])
    def test_get_loan_type_invalid_then_valid(self, mock_input):
        """Should reject non-numeric, out-of-range, and negative inputs before accepting a valid one."""
        self.assertEqual(bls.get_loan_type(), '2')
        self.assertEqual(mock_input.call_count, 4)

    @patch('builtins.input', side_effect=['-100', '0', 'not a number', '50000.75'])
    def test_get_positive_float_invalid_then_valid(self, mock_input):
        """Should reject negative, zero, and string inputs before accepting a positive float."""
        result = bls.get_positive_float("Enter amount: ")
        self.assertAlmostEqual(result, 50000.75)
        self.assertEqual(mock_input.call_count, 4)
        
    @patch('builtins.input', side_effect=['7', '0', '5.5', '6'])
    def test_get_loan_term_invalid_then_valid(self, mock_input):
        """Should reject out-of-range, zero, and float inputs for term."""
        max_term = 6
        result = bls.get_loan_term(max_term)
        self.assertEqual(result, 6)
        self.assertEqual(mock_input.call_count, 4)

    # ----------------------------------------
    # 2. Calculation Logic & Edge Case Tests
    # ----------------------------------------
    def test_calculate_monthly_payment_standard(self):
        """Test a standard, valid loan calculation against a known result."""
        # Housing Loan: $100,000 at 5.2% for 20 years
        self.assertAlmostEqual(bls.calculate_monthly_payment(100000, 5.2, 20), 672.89, places=2)

    def test_calculate_monthly_payment_zero_values(self):
        """Test calculation with zero as principal or term."""
        self.assertEqual(bls.calculate_monthly_payment(0, 5.2, 20), 0)
        self.assertEqual(bls.calculate_monthly_payment(100000, 5.2, 0), 0)

    def test_calculate_monthly_payment_zero_interest(self):
        """Test calculation for a zero-interest loan."""
        # $12,000 at 0% for 1 year should be $1000/month.
        self.assertAlmostEqual(bls.calculate_monthly_payment(12000, 0, 1), 1000.00, places=2)

    def test_calculate_monthly_payment_overflow(self):
        """Test with an extremely large principal that could cause an overflow."""
        # This should be caught by the try-except block and return infinity.
        large_principal = 10**1000
        self.assertEqual(bls.calculate_monthly_payment(large_principal, 5.0, 30), float('inf'))

    def test_calculate_total_interest(self):
        """Test the total interest calculation."""
        # Principal: 200000, Monthly Payment: 1500, Term: 20 years
        # Total Paid: 1500 * 240 = 360000. Interest = 360000 - 200000 = 160000
        self.assertAlmostEqual(bls.calculate_total_interest(200000, 1500, 20), 160000, places=2)

if __name__ == '__main__':
    unittest.main(verbosity=2)
