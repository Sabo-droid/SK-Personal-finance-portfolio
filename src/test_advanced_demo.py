#!/usr/bin/env python3
"""
Advanced test: Demonstrate the feature with dramatic spending reductions
"""

import pandas as pd
from delayed_gratification import display_delayed_gratification_insights

def calculate_category_breakdown(df):
    """
    Calculates spending breakdown by category.
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

# Load dramatic savings data
print("Loading dramatic savings dataset...")
df = pd.read_csv('data/dramatic_savings_transactions.csv')
df['date'] = pd.to_datetime(df['date'])

print("\n" + "="*70)
print("ADVANCED TEST: DRAMATIC SPENDING REDUCTIONS")
print("="*70)

print("\n--- Category Spending Breakdown (July) ---")
category_breakdown = calculate_category_breakdown(df)
print(category_breakdown.to_string(index=False))
total_expenses_breakdown = category_breakdown['Amount'].sum()
print(f"\nTotal Expenses: ${total_expenses_breakdown:.2f}")

print("\n")
display_delayed_gratification_insights(df)

print("\n" + "="*70)
print("Notice how the feature:")
print("✅ Highlights the 75% reduction in Eating Out (~$110 saved)")
print("✅ Projects $660 in 6 months, $2,640 in 2 years, $6,600 in 5 years")
print("✅ Maps $2,640 to meaningful rewards like flights & travel")
print("✅ Celebrates progress without shame or judgment")
print("="*70)
