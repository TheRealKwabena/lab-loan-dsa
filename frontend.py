import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os

from backend import calculate_monthly_payment, calculate_total_interest, save_loan_record
from backend import *

# --- Tkinter Application Class ---

class LoanApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Bank Loan Management System")
        self.geometry("450x600")
        self.resizable(False, False)

        # Style configuration
        self.style = ttk.Style(self)
        self.style.configure('TLabel', font=('Helvetica', 10))
        self.style.configure('TButton', font=('Helvetica', 10, 'bold'))
        self.style.configure('Header.TLabel', font=('Helvetica', 14, 'bold'))

        # To store the details of the last successfully calculated loan
        self.current_loan_details = None

        self._create_widgets()

    def _create_widgets(self):
        """Creates and arranges all the UI widgets in the window."""
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # --- Input Section ---
        input_frame = ttk.LabelFrame(main_frame, text="Loan Details", padding="15")
        input_frame.pack(fill=tk.X)
        input_frame.columnconfigure(1, weight=1)

        # Loan Type
        ttk.Label(input_frame, text="Loan Type:").grid(row=0, column=0, sticky=tk.W, pady=5)
        self.loan_type_var = tk.StringVar()
        self.loan_type_combo = ttk.Combobox(
            input_frame,
            textvariable=self.loan_type_var,
            values=list(LOAN_OPTIONS.keys()),
            state='readonly'
        )
        self.loan_type_combo.grid(row=0, column=1, sticky=tk.EW, padx=5)
        self.loan_type_combo.bind("<<ComboboxSelected>>", self.update_loan_info)

        # Loan Amount
        ttk.Label(input_frame, text="Loan Amount ($):").grid(row=1, column=0, sticky=tk.W, pady=5)
        self.amount_var = tk.StringVar()
        self.amount_entry = ttk.Entry(input_frame, textvariable=self.amount_var)
        self.amount_entry.grid(row=1, column=1, sticky=tk.EW, padx=5)

        # Monthly Income
        ttk.Label(input_frame, text="Monthly Income ($):").grid(row=2, column=0, sticky=tk.W, pady=5)
        self.income_var = tk.StringVar()
        self.income_entry = ttk.Entry(input_frame, textvariable=self.income_var)
        self.income_entry.grid(row=2, column=1, sticky=tk.EW, padx=5)
        
        # Loan Term
        ttk.Label(input_frame, text="Loan Term (Years):").grid(row=3, column=0, sticky=tk.W, pady=5)
        self.term_var = tk.StringVar()
        self.term_entry = ttk.Entry(input_frame, textvariable=self.term_var)
        self.term_entry.grid(row=3, column=1, sticky=tk.EW, padx=5)
        
        # --- Loan Info Display ---
        self.info_label = ttk.Label(input_frame, text="Select a loan type to see details", foreground="blue")
        self.info_label.grid(row=4, column=0, columnspan=2, pady=(10, 5))

        # --- Action Buttons ---
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)
        button_frame.columnconfigure(0, weight=1)
        button_frame.columnconfigure(1, weight=1)
        button_frame.columnconfigure(2, weight=1)

        self.calc_button = ttk.Button(button_frame, text="Calculate Loan", command=self.calculate_loan)
        self.calc_button.grid(row=0, column=0, padx=5, sticky=tk.EW)

        self.save_button = ttk.Button(button_frame, text="Save Loan", command=self.save_loan, state=tk.DISABLED)
        self.save_button.grid(row=0, column=1, padx=5, sticky=tk.EW)
        
        self.reset_button = ttk.Button(button_frame, text="Reset", command=self.reset_form)
        self.reset_button.grid(row=0, column=2, padx=5, sticky=tk.EW)

        # --- Results Section ---
        results_frame = ttk.LabelFrame(main_frame, text="Results", padding="15")
        results_frame.pack(fill=tk.BOTH, expand=True)
        
        self.results_text = tk.Text(results_frame, height=10, width=50, state=tk.DISABLED, font=('Courier', 10))
        self.results_text.pack(fill=tk.BOTH, expand=True)

    def update_loan_info(self, event=None):
        """Updates the info label when a new loan type is selected."""
        loan_name = self.loan_type_var.get()
        if loan_name:
            details = LOAN_OPTIONS[loan_name]
            rate = details['rate']
            max_term = details['max_term']
            self.info_label.config(text=f"Rate: {rate}% | Max Term: {max_term} years")

    def display_results(self, content):
        """Helper function to display text in the results box."""
        self.results_text.config(state=tk.NORMAL)
        self.results_text.delete('1.0', tk.END)
        self.results_text.insert(tk.END, content)
        self.results_text.config(state=tk.DISABLED)

    def calculate_loan(self):
        """Validates inputs and calculates loan details upon button click."""
        # Reset state
        self.save_button.config(state=tk.DISABLED)
        self.current_loan_details = None

        # --- Input Validation ---
        try:
            loan_name = self.loan_type_var.get()
            if not loan_name:
                messagebox.showerror("Input Error", "Please select a loan type.")
                return

            principal = float(self.amount_var.get())
            monthly_income = float(self.income_var.get())
            term = int(self.term_var.get())

            if principal <= 0 or monthly_income <= 0 or term <= 0:
                raise ValueError("Inputs must be positive numbers.")

        except ValueError as e:
            messagebox.showerror("Input Error", f"Invalid input. Please enter valid positive numbers.\nDetails: {e}")
            return
            
        # --- Term Validation ---
        loan_config = LOAN_OPTIONS[loan_name]
        max_term = loan_config['max_term']
        if not validate_term_selection(term, max_term):
            messagebox.showwarning("Term Error", f"Loan term for '{loan_name}' must be between 1 and {max_term} years.")
            return

        # --- Calculation ---
        annual_rate = loan_config['rate']
        monthly_payment = calculate_monthly_payment(principal, annual_rate, term)
        total_interest = calculate_total_interest(principal, monthly_payment, term)
        max_monthly_payment = calculate_max_monthly_payment(monthly_income)

        # --- Display Results ---
        result_str = (
            f"{'Loan Type:':<22} {loan_name}\n"
            f"{'Principal Amount:':<22} ${principal:,.2f}\n"
            f"{'Annual Rate:':<22} {annual_rate}%\n"
            f"{'Loan Term:':<22} {term} years\n"
            f"{'-'*40}\n"
            f"{'MONTHLY PAYMENT:':<22} ${monthly_payment:,.2f}\n"
            f"{'Total Interest:':<22} ${total_interest:,.2f}\n"
            f"{'Max Allowed Payment:':<22} ${max_monthly_payment:,.2f}\n"
            f"{'-'*40}\n"
        )
        
        # --- Debt Ratio Check ---
        if monthly_payment <= max_monthly_payment:
            result_str += "STATUS: APPROVED\nYour payment is within the 50% income limit."
            self.save_button.config(state=tk.NORMAL) # Enable saving
            
            # Store details for saving
            self.current_loan_details = {
                'Loan Type': loan_name,
                'Loan Amount': f"{principal:.2f}",
                'Interest Rate': f"{annual_rate}%",
                'Term': f"{term} years",
                'Monthly Payment': f"{monthly_payment:.2f}",
                'Total Interest': f"{total_interest:.2f}",
                'Status': 'Finalized'
            }
        else:
            result_str += "STATUS: REJECTED - PAYMENT TOO HIGH\n"
            result_str += "Your monthly payment exceeds 50% of your income.\n"
            result_str += "Try reducing the loan amount or increasing the term."

        self.display_results(result_str)

    def save_loan(self):
        """Saves the current loan details to the CSV file."""
        if self.current_loan_details:
            save_loan_record(self.current_loan_details)
            self.reset_form() # Reset after successful save
        else:
            messagebox.showerror("Save Error", "No valid loan details to save. Please calculate a loan first.")

    def reset_form(self):
        """Clears all input fields and results."""
        self.loan_type_var.set('')
        self.amount_var.set('')
        self.income_var.set('')
        self.term_var.set('')
        self.info_label.config(text="Select a loan type to see details")
        self.display_results("")
        self.save_button.config(state=tk.DISABLED)
        self.current_loan_details = None
        self.amount_entry.focus()


if __name__ == "__main__":
    app = LoanApp()
    app.mainloop()