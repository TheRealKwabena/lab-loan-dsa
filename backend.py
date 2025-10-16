# --- Constants and Configuration from the original script ---
# This section remains largely the same, defining the core business logic.
from tkinter import ttk, messagebox
import csv
import os
LOAN_OPTIONS = {
    'Housing Loan': {'rate': 5.2, 'max_term': 25},
    'Auto Loan': {'rate': 7.5, 'max_term': 6},
    'Personal Loan': {'rate': 9.6, 'max_term': 10}
}

DEBT_RATIO_LIMIT = 0.50
CSV_FILE = 'loan_records.csv'
CSV_HEADER = ['Loan Type', 'Loan Amount', 'Interest Rate', 'Term', 'Monthly Payment', 'Total Interest', 'Status']

# --- Core Calculation and File Handling Functions ---
# These functions are copied directly from your script.

def calculate_monthly_payment(principal, annual_rate, term_years):
    """Calculates the monthly loan payment using the standard amortization formula."""
    if principal <= 0 or term_years <= 0:
        return 0
    monthly_rate = (annual_rate / 100) / 12
    num_payments = term_years * 12
    if monthly_rate == 0:
        return principal / num_payments
    try:
        power_term = (1 + monthly_rate)**num_payments
        numerator = principal * monthly_rate * power_term
        denominator = power_term - 1
        return numerator / denominator
    except (ZeroDivisionError, OverflowError):
        return float('inf')

def calculate_total_interest(principal, monthly_payment, term_years):
    """Calculates the total interest paid over the life of the loan."""
    total_paid = monthly_payment * (term_years * 12)
    return total_paid - principal

def save_loan_record(loan_details):
    """Saves the finalized loan record to a CSV file."""
    file_exists = os.path.isfile(CSV_FILE)
    try:
        with open(CSV_FILE, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=CSV_HEADER)
            if not file_exists:
                writer.writeheader()
            writer.writerow(loan_details)
        messagebox.showinfo("Success", f"Loan record successfully saved to {CSV_FILE}.")
    except IOError as e:
        messagebox.showerror("File Error", f"Error: Could not write to file {CSV_FILE}.\n{e}")

def validate_term_selection(term, max_term):

    return 1 <= term <= max_term

def calculate_max_monthly_payment(monthly_income):
    return monthly_income * DEBT_RATIO_LIMIT


def get_loan_type():
    """Prompts the user to select a loan and validates the choice."""
    while True:
        print("\n--- Select a Loan Type ---")
        for key, option in LOAN_OPTIONS.items():
            print(f"{key}: {option['name']}")
        
        choice = input("Enter the number for your desired loan type: ")
        if choice in LOAN_OPTIONS:
            return choice # 
        print("Invalid choice. Please select a valid number from the list.")


def get_positive_float(prompt):
    """""Gets and validates a positive floating-point number from the user."""
    while True:
        try:
            value = float(input(prompt))
            if value > 0:
                return value
            print("Invalid input. Please enter a positive number.")
        except ValueError:
            print("Invalid format. Please enter a numeric value.")

def get_loan_term(max_term):
    """""Gets and validates the loan term, ensuring it's within the allowed maximum.]"""
    while True:
        try:
            prompt = f"Enter the loan term in years (1 - {max_term} years): "
            term = int(input(prompt))
            if 1 <= term <= max_term:
                return term
            print(f"Invalid term. Please enter a value between 1 and {max_term}.")
        except ValueError:
            print("Invalid format. Please enter a whole number for the years.")

