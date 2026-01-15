
# Copilot prompt:
# Write Python code using pandas that:
# - loads a CSV file called data/transactions.csv
# - ensures the date column is parsed as datetime
# - validates that columns are date, category, amount
# - raises a clear error if any column is missing
import pandas as pd
from datetime import datetime

# Interactive file input
print("--- Personal Finance Analyzer ---")
try:
    file_path = input("Enter the path to your transactions CSV file (e.g., '../data/transactions.csv'): ")
    
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

def project_future_cashflow(monthly_cashflow, months_ahead, required_savings):
    """
    Projects future monthly cash flow by adding savings as expense.
    
    Args:
        monthly_cashflow: Historical DataFrame
        months_ahead: Number of months to project
        required_savings: Monthly savings amount to add as expense
    
    Returns:
        DataFrame with projected months
    """
    if monthly_cashflow.empty:
        return pd.DataFrame()
    
    # Use current date and average values as base for projection
    current_month = pd.to_datetime(datetime.now()).strftime('%Y-%m')
    avg_income = monthly_cashflow['income'].mean()
    avg_expenses = monthly_cashflow['expenses'].mean()
    avg_net = monthly_cashflow['net_cashflow'].mean()
    
    projections = []
    
    for i in range(1, months_ahead + 1):
        projected_date = pd.to_datetime(current_month) + pd.offsets.MonthEnd(i)
        projected_month = projected_date.strftime('%Y-%m')
        projected = {
            'month': projected_month,
            'income': avg_income,
            'expenses': avg_expenses + required_savings,
            'net_cashflow': avg_income - (avg_expenses + required_savings)
        }
        projections.append(projected)
    
    return pd.DataFrame(projections)

# Calculate monthly cash flow
monthly_cashflow = calculate_monthly_cashflow(df)
print("\nMonthly Cash Flow Summary:")
print(monthly_cashflow)

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
print(f"\nEmergency Fund Runway: {runway:.1f} months (based on ${total_savings:.2f} savings from data and average monthly expenses of ${monthly_cashflow['expenses'].mean():.2f})")




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
    
    required_monthly_savings = goal_amount / months_to_target
    
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
        print("4. Savings Goal Planner")
        print("5. Future Cash Flow Projection (No Changes)")
        print("6. What-If Scenario Analysis")
        print("7. Category Spending Breakdown")
        print("0. Exit")
        
        choice = input("\nEnter your choice (0-7): ").strip()
        
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
            print("\n--- Savings Goal Planner ---")
            try:
                goal_amount = float(input("Enter your savings goal amount: $"))
                target_date = input("Enter your target date (YYYY-MM-DD): ")
                
                savings_plan = plan_savings_goal(goal_amount, target_date, monthly_cashflow)
                
                if 'error' in savings_plan:
                    print(f"Error: {savings_plan['error']}")
                else:
                    print(f"\nSavings Goal Plan:")
                    print(f"Goal Amount: ${goal_amount:.2f}")
                    print(f"Target Date: {target_date}")
                    print(f"Months to Target: {savings_plan['months_to_target']:.1f}")
                    print(f"Required Monthly Savings: ${savings_plan['required_monthly_savings']:.2f}")
                    print(f"Achievable: {'Yes' if savings_plan['achievable'] else 'No'}")
                    print(f"\nProjected Cash Flow with Savings Goal:")
                    print(savings_plan['updated_cashflow'])
            except ValueError:
                print("Invalid input. Please enter valid values.")
                
        elif choice == '5':
            print("\n--- Future Cash Flow Projection (No Changes) ---")
            try:
                months = int(input("How many months to project? "))
                current_date = pd.to_datetime(datetime.now())
                avg_income = monthly_cashflow['income'].mean()
                avg_expenses = monthly_cashflow['expenses'].mean()
                
                projections = []
                cumulative = 0
                for i in range(1, months + 1):
                    future_date = current_date + pd.DateOffset(months=i)
                    projected_month = future_date.strftime('%Y-%m')
                    net = avg_income - avg_expenses
                    cumulative += net
                    
                    projections.append({
                        'month': projected_month,
                        'income': avg_income,
                        'expenses': avg_expenses,
                        'net_cashflow': net,
                        'cumulative_savings': cumulative
                    })
                
                projection_df = pd.DataFrame(projections)
                print("\nProjected Cash Flow:")
                print(projection_df.to_string(index=False))
                print(f"\nFinal Cumulative Savings after {months} months: ${cumulative:.2f}")
            except ValueError:
                print("Invalid input. Please enter a number.")
                
        elif choice == '6':
            print("\n--- What-If Scenario Analysis ---")
            try:
                months = int(input("How many months to project? "))
                print("\nScenario Types:")
                print("1. Decrease Spending")
                print("2. Increase Savings")
                print("3. Both (balanced approach)")
                scenario_choice = input("Choose scenario (1-3): ").strip()
                
                scenario_map = {'1': 'decrease_spending', '2': 'increase_savings', '3': 'both'}
                scenario_type = scenario_map.get(scenario_choice, 'decrease_spending')
                
                if scenario_type == 'decrease_spending':
                    amount = float(input("Enter amount to decrease spending by: $"))
                    desc = f"Decrease spending by ${amount}"
                elif scenario_type == 'increase_savings':
                    amount = float(input("Enter amount to increase savings by: $"))
                    desc = f"Increase savings by ${amount}"
                else:
                    amount = float(input("Enter total amount to adjust (split between income/expenses): $"))
                    desc = f"Balanced adjustment: +${amount/2} income, -${amount/2} expenses"
                
                scenario_cf = run_what_if_scenario(monthly_cashflow, months, scenario_type, amount)
                
                # Compare with baseline (no changes)
                current_date = pd.to_datetime(datetime.now())
                avg_income = monthly_cashflow['income'].mean()
                avg_expenses = monthly_cashflow['expenses'].mean()
                baseline_cumulative = (avg_income - avg_expenses) * months
                scenario_cumulative = scenario_cf['cumulative_savings'].iloc[-1]
                difference = scenario_cumulative - baseline_cumulative
                
                print(f"\n--- What-If Scenario: {desc} ---")
                print(scenario_cf.to_string(index=False))
                print(f"\nComparison:")
                print(f"Baseline Final Worth (no changes): ${baseline_cumulative:.2f}")
                print(f"Scenario Final Worth: ${scenario_cumulative:.2f}")
                print(f"Difference: ${difference:.2f} ({(difference/baseline_cumulative*100) if baseline_cumulative != 0 else 0:.1f}%)")
            except ValueError:
                print("Invalid input. Please enter valid values.")
                
        elif choice == '7':
            print("\n--- Category Spending Breakdown ---")
            category_breakdown = calculate_category_breakdown(df)
            print(category_breakdown.to_string(index=False))
            total_expenses_breakdown = category_breakdown['Amount'].sum()
            print(f"\nTotal Expenses: ${total_expenses_breakdown:.2f}")
            
        elif choice == '0':
            print("\nThank you for using Personal Finance Analyzer. Goodbye!")
            break
            
        else:
            print("Invalid choice. Please enter 0-7.")

# Run main menu
main_menu()


