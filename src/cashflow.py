
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
    
    # Load the CSV file (assume headers are present)
    df = pd.read_csv(file_path)
    
    # Default required columns
    required_columns = ['date', 'category', 'amount']
    column_mapping = {}
    
    # Check for missing columns and prompt for alternatives
    for col in required_columns:
        if col not in df.columns:
            alt_col = input(f"Column '{col}' not found. Enter the actual column name (or press Enter to skip): ")
            if alt_col and alt_col in df.columns:
                column_mapping[col] = alt_col
            else:
                raise ValueError(f"Required column '{col}' is missing and no valid alternative provided.")
    
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
except ValueError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")

# The dataframe is now loaded and validated





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
total_savings = calculate_total_savings(df)

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

# Interactive savings goal planning
print("\n--- Savings Goal Planner ---")
try:
    goal_amount = float(input("Enter your savings goal amount: $"))
    target_date = input("Enter your target date (YYYY-MM-DD): ")
    
    savings_plan = plan_savings_goal(goal_amount, target_date, monthly_cashflow)

    if 'error' in savings_plan:
        print(f"\nSavings Goal Error: {savings_plan['error']}")
    else:
        print(f"\nSavings Goal Plan:")
        print(f"Goal Amount: ${goal_amount}")
        print(f"Target Date: {target_date}")
        print(f"Months to Target: {savings_plan['months_to_target']:.1f}")
        print(f"Required Monthly Savings: ${savings_plan['required_monthly_savings']:.2f}")
        print(f"Achievable: {'Yes' if savings_plan['achievable'] else 'No'} (based on average net cash flow of ${monthly_cashflow['net_cashflow'].mean():.2f})")
        
        print("\nUpdated Monthly Cash Flow (with savings goal as expense):")
        print(savings_plan['updated_cashflow'])
except ValueError:
    print("Invalid input. Please enter a valid number for the goal amount and date in YYYY-MM-DD format.")



# RISK AND UNCERTAINTY


