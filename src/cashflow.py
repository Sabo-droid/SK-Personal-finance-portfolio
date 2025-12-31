# Copilot prompt:
# Write Python code using pandas that:
# - loads a CSV file called data/transactions.csv
# - ensures the date column is parsed as datetime
# - validates that columns are date, category, amount
# - raises a clear error if any column is missing
import pandas as pd
from datetime import datetime

# Load the CSV file with date parsing
df = pd.read_csv('../data/transactions.csv', parse_dates=['date'])

# Required columns
required_columns = ['date', 'category', 'amount']

# Check if all required columns are present
missing_columns = [col for col in required_columns if col not in df.columns]
if missing_columns:
    raise ValueError(f"Missing required columns: {', '.join(missing_columns)}")

# The dataframe is now loaded and validated
print("Data loaded successfully!")
print(df.head())



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

# Calculate monthly cash flow
monthly_cashflow = calculate_monthly_cashflow(df)
print("\nMonthly Cash Flow Summary:")
print(monthly_cashflow)




# Copilot prompt:
# Add a function that:
# - calculates average monthly expenses
# - computes emergency fund runway = savings / monthly expenses
# - returns number of months the user can survive without income


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

# Example usage with placeholder savings
savings = 5000  # Replace with actual savings amount
runway = calculate_emergency_runway(monthly_cashflow, savings)
print(f"\nEmergency Fund Runway: {runway:.1f} months (based on ${savings} savings and average monthly expenses of ${monthly_cashflow['expenses'].mean():.2f})")




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
    
    # Integrate as new expense category in the cash flow model
    updated_cashflow = monthly_cashflow.copy()
    updated_cashflow['expenses'] += required_monthly_savings  # Add savings as expense
    updated_cashflow['net_cashflow'] = updated_cashflow['income'] - updated_cashflow['expenses']
    
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


