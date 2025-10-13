import csv
import os

# --- Loan Configuration ---
# Defines the available loan types with their specific interest rates and maximum terms.
LOAN_OPTIONS = {
    '1': {'name': 'Housing Loan', 'rate': 5.2, 'max_term': 25}, # [cite: 4]
    '2': {'name': 'Auto Loan', 'rate': 7.5, 'max_term': 6},     # [cite: 5]
    '3': {'name': 'Personal Loan', 'rate': 9.6, 'max_term': 10}  # [cite: 6]
}

#Constants and variables of the program
DEBT_RATIO_LIMIT = 0.50 
CSV_FILE = 'loan_records.csv'
CSV_HEADER = ['Loan Type', 'Loan Amount', 'Interest Rate', 'Term', 'Monthly Payment', 'Total Interest', 'Status'] # [cite: 78]

# --- Core Calculation Functions ---

def calculate_monthly_payment(principal: int, annual_rate: int, term_years: int):
    """
    ""Calculates the monthly loan payment using the standard amortization formula. [cite: 22, 85]
    ""The formula is M = P * [r(1+r)^n] / [(1+r)^n - 1]. [cite: 23, 36, 92]
    """
    if principal <= 0 or term_years <= 0:
        return 0

    monthly_rate = (annual_rate / 100) / 12 
    num_payments = term_years * 12          

    if monthly_rate == 0: 
        return principal / num_payments

    # This part implements the core logic of the loan payment formula.
    try:
        power_term = (1 + monthly_rate)**num_payments
        numerator = principal * monthly_rate * power_term
        denominator = power_term - 1
        return numerator / denominator
    except (ZeroDivisionError, OverflowError):
        # Handles potential math errors with unusual inputs
        return float('inf')

def calculate_total_interest(principal, monthly_payment, term_years):
    """Calculates the total interest paid over the life of the loan."""
    total_paid = monthly_payment * (term_years * 12)
    return total_paid - principal

# --- User Input and Validation ---

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

# --- File Handling ---

def save_loan_record(loan_details):
    """""Saves the finalized loan record to a CSV file"""
    file_exists = os.path.isfile(CSV_FILE)
    try:
        with open(CSV_FILE, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=CSV_HEADER)
            if not file_exists:
                writer.writeheader()
            writer.writerow(loan_details)
        print(f" Loan record successfully saved to {CSV_FILE}.")
    except IOError as e:
        print(f" Error: Could not write to file {CSV_FILE}. {e}")


# --- Main Application Logic ---

def main():
    """Main function to run the bank loan management system simulation."""
    print("Welcome to the Bank Loan Management System!")

    while True:
        loan_choice_key = get_loan_type()
        loan_config = LOAN_OPTIONS[loan_choice_key]
        loan_name = loan_config['name']
        annual_rate = loan_config['rate']
        max_term = loan_config['max_term']

        principal = get_positive_float(f"Enter the loan amount for the {loan_name}: $")
        monthly_income = get_positive_float("Enter your total monthly income: $")
        term = get_loan_term(max_term)

        # ""Loop to handle debt ratio check and user adjustments
        while True:
            monthly_payment = calculate_monthly_payment(principal, annual_rate, term)
            max_monthly_payment = monthly_income * DEBT_RATIO_LIMIT

            print("\n--- Calculating Your Loan ---")
            print(f"Monthly Payment: ${monthly_payment:,.2f}")
            print(f"Your maximum allowed monthly payment (50% of income): ${max_monthly_payment:,.2f}")

            if monthly_payment <= max_monthly_payment: # [cite: 30]
                print("\n Congratulations! Your monthly payment is within the allowed limit.")
                break
            else:
                print(f"\n Warning: Your monthly payment exceeds 50% of your income.") 
                
                # Offer options if the user can extend the loan term
                if term < max_term:
                    print(f"You can try to lower your payment by extending the term (current: {term}, max: {max_term}).") # [cite: 32, 96]
                    adjust_choice = input("Choose an option: (1) Adjust Term, (2) Change Loan Amount, (3) Cancel Loan: ").strip()
                    if adjust_choice == '1':
                        term = get_loan_term(max_term)
                    elif adjust_choice == '2':
                        principal = get_positive_float("Enter the new loan amount: $") 
                    else:
                        principal = None; 
                        break # Flag to cancel
                else: # Offer options when max term is already reached
                    print(f"You have reached the maximum term of {max_term} years for this loan.")
                    adjust_choice = input("Choose an option: (1) Change Loan Amount, (2) Cancel Loan: ").strip()
                    if adjust_choice == '1':
                        principal = get_positive_float("Enter the new loan amount: $")
                    else:
                        principal = None; break
        
        # ""Display final summary and save if approved by the user
        if principal is not None:
            total_interest = calculate_total_interest(principal, monthly_payment, term)
            
            print("\n--- Final Loan Summary ---")
            print(f"{'Loan Type:':<22} {loan_name}")
            print(f"{'Principal Amount:':<22} ${principal:,.2f}")
            print(f"{'Annual Interest Rate:':<22} {annual_rate}%")
            print(f"{'Loan Term:':<22} {term} years")
            print("-" * 35)
            print(f"{'Monthly Payment:':<22} ${monthly_payment:,.2f}")
            print(f"{'Total Interest Paid:':<22} ${total_interest:,.2f}")
            print("-" * 35)

            proceed = input("Do you want to finalize this loan? (yes/no): ").lower().strip()
            if proceed == 'yes':
                loan_record = {
                    'Loan Type': loan_name, 'Loan Amount': f"{principal:.2f}",
                    'Interest Rate': f"{annual_rate}%", 'Term': f"{term} years",
                    'Monthly Payment': f"{monthly_payment:.2f}", 'Total Interest': f"{total_interest:.2f}",
                    'Status': 'Finalized'
                }
                save_loan_record(loan_record)
            else:
                print("\nLoan application canceled. The record was not saved.")

        # Ask to process another loan
        if input("\nProcess another loan? (yes/no): ").lower().strip() != 'yes':
            print("\nThank you for using the Bank Loan Management System. Goodbye!")
            break

if __name__ == "__main__":
    main()