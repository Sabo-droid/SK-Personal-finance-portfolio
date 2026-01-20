
import pandas as pd
from datetime import datetime
import os
from delayed_gratification import display_delayed_gratification_insights

# Helper function to create sample transactions CSV if it doesn't exist
def create_sample_transactions(file_path):
    """Create a sample transactions CSV file for testing if it doesn't exist."""
    if os.path.exists(file_path):
        return
    
    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    
    sample_data = {
        'date': [
            '2025-06-05', '2025-06-12', '2025-06-15', '2025-06-19',
            '2025-06-26', '2025-06-03', '2025-06-10', '2025-06-17',
            '2025-06-24', '2025-06-30'
        ],
        'category': [
            'Part-time Job', 'Food', 'Rent', 'Scholarship',
            'Books', 'Utilities', 'Entertainment', 'Allowance',
            'Food', 'Clothing'
        ],
        'amount': [
            335.50, -85.40, -538.88, 985.75,
            -90.59, -43.77, -56.81, 63.13,
            -64.29, -98.93
        ]
    }
    
    df_sample = pd.DataFrame(sample_data)
    df_sample.to_csv(file_path, index=False)
    print(f"Created sample transactions file at {file_path}")

# Interactive file input
print("--- Personal Finance Analyzer ---")
try:
    DEFAULT_PATH = "data/sample_transactions.csv"
    user_input = input(
        f"Enter path to transactions CSV file\n"
        f"[Press Enter to use '{DEFAULT_PATH}']: "
    ).strip()
    
    file_path = user_input if user_input else DEFAULT_PATH
    
    # If using default path, create sample file if it doesn't exist
    if file_path == DEFAULT_PATH:
        create_sample_transactions(file_path)
    
    print(f"\nLoading transactions from: {file_path}")
    
    # Load the CSV file with encoding and delimiter error handling
    df = None
    encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
    delimiters = [',', ';', '\t', '|']
    
    for encoding in encodings:
        for delimiter in delimiters:
            try:
                df = pd.read_csv(file_path, encoding=encoding, delimiter=delimiter, on_bad_lines='skip', engine='python')
                if not df.empty:
                    print(f"File loaded with {encoding} encoding and '{delimiter}' delimiter.")
                    break
            except (UnicodeDecodeError, LookupError, pd.errors.ParserError):
                continue
        if df is not None and not df.empty:
            break
    
    # If still no luck, try with error_bad_lines=False (older pandas)
    if df is None or df.empty:
        for encoding in encodings:
            try:
                df = pd.read_csv(file_path, encoding=encoding, error_bad_lines=False)
                if not df.empty:
                    print(f"File loaded with {encoding} encoding (skipping bad lines).")
                    break
            except (UnicodeDecodeError, LookupError):
                continue
    
    if df is None or df.empty:
        raise ValueError("Could not read CSV file. Tried multiple encodings and delimiters. Please ensure the file is a valid CSV.")
    
    # Remove empty columns
    df = df.dropna(axis=1, how='all')
    
    # Standardize column names (lowercase and strip whitespace)
    df.columns = df.columns.str.lower().str.strip()
    
    print(f"Available columns: {list(df.columns)}")
    
    # Default required columns
    required_columns = ['date', 'category', 'amount']
    column_mapping = {}
    
    # Create flexible mapping for common column name variations
    column_aliases = {
        'date': ['date', 'transaction_date', 'trans_date'],
        'category': ['category', 'description', 'type', 'transaction_type'],
        'amount': ['amount', 'value', 'transaction_amount']
    }
    
    # Try to auto-map columns
    for required_col, aliases in column_aliases.items():
        found = False
        for alias in aliases:
            if alias in df.columns:
                if alias != required_col:
                    column_mapping[alias] = required_col
                found = True
                break
        
        if not found:
            print(f"Column '{required_col}' not found. Available: {list(df.columns)}")
            alt_col = input(f"Enter the actual column name for '{required_col}': ")
            if alt_col and alt_col in df.columns:
                column_mapping[alt_col] = required_col
            else:
                raise ValueError(f"Required column '{required_col}' is missing.")
    
    # Rename columns if alternatives were provided
    if column_mapping:
        df = df.rename(columns=column_mapping)
    
    # Now parse date and validate
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    if df['date'].isnull().any():
        raise ValueError("Invalid date values found. Ensure dates are in a parseable format.")
    
    # Validate 'amount' as numeric
    df['amount'] = pd.to_numeric(df['amount'], errors='coerce')
    if df['amount'].isnull().any():
        raise ValueError("Invalid 'amount' values found. Ensure all amounts are numeric.")
    
    print("Data loaded successfully!")
    print(df.head())
    
except FileNotFoundError:
    print("Error: File not found. Please check the path and try again.")
    df = None
except ValueError as e:
    print(f"Error: {e}")
    df = None
except Exception as e:
    print(f"Unexpected error: {e}")
    df = None

# The dataframe is now loaded and validated
if df is None:
    print("Cannot proceed without valid data. Exiting.")
    exit()




# Copilot prompt:
# Create a function that:
# - groups transactions by month
# - calculates total income, total expenses, and net cash flow
# - returns a clean DataFrame with columns:
#   month, income, expenses, net_cashflow

def calculate_monthly_cashflow(df):
    """
    Groups transactions by month and calculates total income, total expenses, and net cash flow.
    
    Returns a DataFrame with columns: month, income, expenses, net_cashflow
    """
    # Create month column
    df['month'] = df['date'].dt.to_period('M')
    
    # Group by month and aggregate
    result = df.groupby('month')['amount'].agg(
        income=lambda x: x[x > 0].sum(),
        expenses=lambda x: -x[x < 0].sum(),  # Make expenses positive
        net_cashflow='sum'
    ).reset_index()
    
    # Convert month to string for cleaner display
    result['month'] = result['month'].astype(str)
    
    return result

def project_future_cashflow(monthly_cashflow, months_ahead, required_savings=0):
    """
    Projects future monthly cash flow by adding savings as expense.
    
    Args:
        monthly_cashflow: Historical DataFrame
        months_ahead: Number of months to project (will be converted to int)
        required_savings: Monthly savings amount to add as expense
    
    Returns:
        DataFrame with projected months
    """
    if monthly_cashflow.empty:
        return pd.DataFrame()
    
    current_date = pd.to_datetime(datetime.now())
    avg_income = monthly_cashflow['income'].mean()
    avg_expenses = monthly_cashflow['expenses'].mean()
    months_to_project = int(months_ahead)
    
    projections = []
    cumulative = 0
    
    for i in range(1, months_to_project + 1):
        future_date = current_date + pd.DateOffset(months=i)
        projected_month = future_date.strftime('%Y-%m')
        adjusted_expenses = avg_expenses + required_savings
        net = avg_income - adjusted_expenses
        cumulative += net
        
        projected = {
            'month': projected_month,
            'income': avg_income,
            'expenses': adjusted_expenses,
            'net_cashflow': net,
            'cumulative_savings': cumulative
        }
        projections.append(projected)
    
    return pd.DataFrame(projections)

# Calculate monthly cash flow
monthly_cashflow = calculate_monthly_cashflow(df)

def calculate_total_savings(df):
    """
    Calculates total savings as the cumulative sum of net cash flow.
    Assumes savings accumulates from positive net cash flows.
    
    Args:
        df: DataFrame with 'amount' column
    
    Returns:
        Total savings amount
    """
    # Calculate net cash flow cumulatively
    df_sorted = df.sort_values('date')
    df_sorted['cumulative_net'] = df_sorted['amount'].cumsum()
    # Savings is the positive cumulative net (or 0 if negative)
    total_savings = max(0, df_sorted['cumulative_net'].iloc[-1])
    return total_savings

# Calculate total savings from data
if df is not None:
    total_savings = calculate_total_savings(df)
else:
    total_savings = 0
    print("\nCannot proceed without valid data.")
    exit()

def calculate_emergency_runway(monthly_cashflow, savings):
    """
    Calculates the emergency fund runway in months.
    
    Args:
        monthly_cashflow: DataFrame with 'expenses' column
        savings: Current savings amount
    
    Returns:
        Number of months the user can survive without income
    """
    avg_monthly_expenses = monthly_cashflow['expenses'].mean()
    
    if avg_monthly_expenses == 0:
        return float('inf')  # Infinite runway if no expenses
    
    runway_months = savings / avg_monthly_expenses
    return runway_months

# Update emergency runway to use calculated savings
runway = calculate_emergency_runway(monthly_cashflow, total_savings)




# Copilot prompt:
# Write code that:
# - accepts a savings goal amount and target date
# - calculates required monthly savings
# - integrates this as a new expense category in the cash flow model
# - checks whether the goal is achievable under current net cash flow

def plan_savings_goal(goal_amount, target_date_str, monthly_cashflow):
    """
    Plans a savings goal and integrates it into the cash flow model.
    
    Args:
        goal_amount: The target savings amount
        target_date_str: Target date as string (e.g., '2025-12-31')
        monthly_cashflow: DataFrame with cash flow data
    
    Returns:
        Dict with required monthly savings, achievability, and updated cash flow
    """
    target_date = pd.to_datetime(target_date_str)
    current_date = datetime.now()
    
    # Calculate months to target (approximate)
    days_to_target = (target_date - current_date).days
    if days_to_target <= 0:
        return {"error": "Target date is in the past"}
    
    months_to_target = days_to_target / 30.44  # Average days per month
    
    # Calculate remaining amount needed (accounting for existing savings)
    remaining_needed = goal_amount - total_savings
    
    if remaining_needed <= 0:
        required_monthly_savings = 0
    else:
        required_monthly_savings = remaining_needed / months_to_target
    
    # Check achievability: can we save this amount given current net cash flow?
    avg_net_cashflow = monthly_cashflow['net_cashflow'].mean()
    achievable = required_monthly_savings <= avg_net_cashflow
    
    # Project future cash flow with savings as expense
    updated_cashflow = project_future_cashflow(monthly_cashflow, int(months_to_target), required_monthly_savings)
    
    return {
        'required_monthly_savings': required_monthly_savings,
        'achievable': achievable,
        'months_to_target': months_to_target,
        'updated_cashflow': updated_cashflow
    }

def calculate_category_breakdown(df):
    """
    Calculates spending breakdown by category.
    
    Returns a DataFrame with category totals and percentages
    """
    category_totals = df.groupby('category')['amount'].sum().sort_values()
    expenses_only = category_totals[category_totals < 0]
    expenses_only = -expenses_only  # Make positive for display
    total_expenses = expenses_only.sum()
    
    result = pd.DataFrame({
        'Category': expenses_only.index,
        'Amount': expenses_only.values,
        'Percentage': (expenses_only.values / total_expenses * 100).round(2)
    }).reset_index(drop=True)
    
    return result

def run_what_if_scenario(monthly_cashflow, months_projection, scenario_type, scenario_amount):
    """
    Runs a what-if scenario and projects cash flow.
    
    Args:
        monthly_cashflow: Historical monthly cash flow DataFrame
        months_projection: Number of months to project
        scenario_type: 'decrease_spending', 'increase_savings', or 'both'
        scenario_amount: Amount to adjust by
    
    Returns:
        Projected cash flow with scenarios
    """
    current_date = pd.to_datetime(datetime.now())
    avg_income = monthly_cashflow['income'].mean()
    avg_expenses = monthly_cashflow['expenses'].mean()
    
    projections = []
    
    for i in range(1, int(months_projection) + 1):
        future_date = current_date + pd.DateOffset(months=i)
        projected_month = future_date.strftime('%Y-%m')
        
        # Calculate adjusted values based on scenario
        if scenario_type == 'decrease_spending':
            adjusted_expenses = avg_expenses - scenario_amount
            adjusted_income = avg_income
        elif scenario_type == 'increase_savings':
            adjusted_expenses = avg_expenses + scenario_amount
            adjusted_income = avg_income
        else:  # both
            adjusted_expenses = avg_expenses - (scenario_amount / 2)
            adjusted_income = avg_income + (scenario_amount / 2)
        
        projected = {
            'month': projected_month,
            'income': adjusted_income,
            'expenses': adjusted_expenses,
            'net_cashflow': adjusted_income - adjusted_expenses,
            'cumulative_savings': 0  # Will be calculated
        }
        projections.append(projected)
    
    result_df = pd.DataFrame(projections)
    result_df['cumulative_savings'] = result_df['net_cashflow'].cumsum()
    
    return result_df

# Main menu system
def main_menu():
    """Interactive menu for personal finance analyzer."""
    
    print("\n" + "="*50)
    print("     PERSONAL FINANCE ANALYZER - MAIN MENU")
    print("="*50)
    
    while True:
        print("\nChoose an option:")
        print("1. Monthly Cash Flow Summary")
        print("2. Total Savings")
        print("3. Emergency Fund Runway")
        print("4. Scenario Projection & Analysis")
        print("5. Category Spending Breakdown")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-5): ").strip()
        
        if choice == '1':
            print("\n--- Monthly Cash Flow Summary ---")
            print(monthly_cashflow)
            
        elif choice == '2':
            print(f"\n--- Total Savings ---")
            print(f"Total Savings from Data: ${total_savings:.2f}")
            
        elif choice == '3':
            print(f"\n--- Emergency Fund Runway ---")
            print(f"Runway: {runway:.1f} months")
            print(f"Savings: ${total_savings:.2f}")
            print(f"Avg Monthly Expenses: ${monthly_cashflow['expenses'].mean():.2f}")
            
        elif choice == '4':
            print("\n--- Scenario Projection & Analysis ---")
            try:
                print("\nChoose a scenario:")
                print("1. No change")
                print("2. Change monthly income")
                print("3. Change monthly expenses")
                print("4. Change both income and expenses")
                scenario_choice = input("Enter scenario choice (1-4): ").strip()

                current_date = pd.to_datetime(datetime.now())
                avg_income = monthly_cashflow['income'].mean()
                avg_expenses = monthly_cashflow['expenses'].mean()

                # Determine adjusted income/expenses based on scenario (ask change immediately)
                new_income = avg_income
                new_expenses = avg_expenses

                if scenario_choice == '1':
                    scenario_desc = "No change"
                elif scenario_choice == '2':
                    change = float(input("Enter income change amount (use + or - as needed, e.g. +500 or -300): $"))
                    new_income = avg_income + change
                    scenario_desc = f"Income change: {change:+.2f} (now ${new_income:.2f})"
                elif scenario_choice == '3':
                    change = float(input("Enter expense change amount (use + or - as needed, e.g. +200 or -100): $"))
                    new_expenses = avg_expenses + change
                    scenario_desc = f"Expense change: {change:+.2f} (now ${new_expenses:.2f})"
                elif scenario_choice == '4':
                    inc = float(input("Enter income change (use + or - as needed): $"))
                    exp = float(input("Enter expense change (use + or - as needed): $"))
                    new_income = avg_income + inc
                    new_expenses = avg_expenses + exp
                    scenario_desc = f"Income change: {inc:+.2f}, Expense change: {exp:+.2f} (now ${new_income:.2f}, ${new_expenses:.2f})"
                else:
                    print("Invalid scenario choice.")
                    continue

                # Ask what the user wants to see (after change inputs)
                print("\nWhat would you like to see?")
                print("1. Projected cumulative savings after X months")
                print("2. Check whether a savings goal is achievable")
                view_choice = input("Enter choice (1-2): ").strip()

                # If user wants cumulative projection
                if view_choice == '1':
                    months = int(input("How many months to project? "))
                    projections = []
                    for i in range(1, months + 1):
                        future_date = current_date + pd.DateOffset(months=i)
                        projected_month = future_date.strftime('%Y-%m')
                        net = new_income - new_expenses
                        projections.append({
                            'month': projected_month,
                            'income': new_income,
                            'expenses': new_expenses,
                            'net_cashflow': net
                        })

                    projection_df = pd.DataFrame(projections)
                    projection_df['cumulative_savings'] = projection_df['net_cashflow'].cumsum()

                    baseline_net = avg_income - avg_expenses
                    baseline_cumulative = baseline_net * months
                    scenario_cumulative = (new_income - new_expenses) * months

                    print(f"\n--- Scenario: {scenario_desc} ---")
                    print(projection_df.to_string(index=False))
                    print(f"\nFinal Cumulative Savings after {months} months: ${projection_df['cumulative_savings'].iloc[-1]:.2f}")
                    if scenario_choice != '1':
                        difference = scenario_cumulative - baseline_cumulative
                        print(f"\nComparison to Baseline:")
                        print(f"Baseline Final Worth: ${baseline_cumulative:.2f}")
                        print(f"Scenario Final Worth: ${scenario_cumulative:.2f}")
                        print(f"Difference: ${difference:.2f} ({(difference/abs(baseline_cumulative)*100) if baseline_cumulative != 0 else 0:.1f}%)")

                # If user wants to check savings goal feasibility
                elif view_choice == '2':
                    goal_amount = float(input("Enter savings goal amount: $"))
                    target_input = input("Enter target date (YYYY-MM-DD) or number of months: ").strip()
                    # try parse as date first
                    try:
                        target_date = pd.to_datetime(target_input)
                        days_to_target = (target_date - current_date).days
                        if days_to_target <= 0:
                            print("Target date is in the past.")
                            continue
                        months_to_target = days_to_target / 30.44
                    except Exception:
                        # treat as months
                        months_to_target = float(target_input)

                    remaining_needed = goal_amount - total_savings
                    if remaining_needed <= 0:
                        required_monthly = 0.0
                    else:
                        required_monthly = remaining_needed / months_to_target

                    projected_monthly_net = new_income - new_expenses
                    achievable = required_monthly <= projected_monthly_net
                    surplus = projected_monthly_net - required_monthly

                    print(f"\nSavings Goal Check under scenario: {scenario_desc}")
                    print(f"Goal Amount: ${goal_amount:.2f}")
                    print(f"Months to Target: {months_to_target:.2f}")
                    print(f"Remaining Needed (after existing savings of ${total_savings:.2f}): ${remaining_needed:.2f}")
                    print(f"Required Monthly Savings: ${required_monthly:.2f}")
                    print(f"Projected Monthly Net Cash Flow under scenario: ${projected_monthly_net:.2f}")
                    print(f"Achievable: {'Yes' if achievable else 'No'}")
                    if achievable:
                        print(f"Surplus per month: ${surplus:.2f}")
                    else:
                        print(f"Shortfall per month: ${-surplus:.2f}")

                else:
                    print("Invalid view choice.")
                    continue

            except ValueError:
                print("Invalid input. Please enter valid values.")
                
        elif choice == '5':
            print("\n--- Category Spending Breakdown ---")
            category_breakdown = calculate_category_breakdown(df)
            print(category_breakdown.to_string(index=False))
            total_expenses_breakdown = category_breakdown['Amount'].sum()
            print(f"\nTotal Expenses: ${total_expenses_breakdown:.2f}")
            
            # Display Delayed Gratification Insights
            display_delayed_gratification_insights(df)
            
        elif choice == '0':
            print("\nThank you for using Personal Finance Analyzer. Goodbye!")
            break
            
        else:
            print("Invalid choice. Please enter 0-5.")

# Run main menu
main_menu()


