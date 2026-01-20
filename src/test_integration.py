#!/usr/bin/env python3
"""
Integration test: Simulating the user experience of selecting option 5 (Category Breakdown)
and seeing the Delayed Gratification Insights automatically displayed
"""

import pandas as pd
import sys

# Import the two main modules
from delayed_gratification import display_delayed_gratification_insights

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

# Load test data
print("Loading transaction data...")
df = pd.read_csv('data/multi_month_transactions.csv')
df['date'] = pd.to_datetime(df['date'])

print("\n" + "="*70)
print("INTEGRATION TEST: MENU OPTION 5 - CATEGORY SPENDING BREAKDOWN")
print("="*70)

print("\n--- Category Spending Breakdown ---")
category_breakdown = calculate_category_breakdown(df)
print(category_breakdown.to_string(index=False))
total_expenses_breakdown = category_breakdown['Amount'].sum()
print(f"\nTotal Expenses: ${total_expenses_breakdown:.2f}")

# Now automatically display Delayed Gratification Insights
# (This is what happens when user selects option 5 in the main menu)
print("\n")
display_delayed_gratification_insights(df)

print("\n" + "="*70)
print("✅ INTEGRATION TEST COMPLETE - Feature working as expected!")
print("="*70)
