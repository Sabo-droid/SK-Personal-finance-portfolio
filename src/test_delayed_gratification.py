#!/usr/bin/env python3
"""
Test script for Delayed Gratification Insights feature
"""

import pandas as pd
from delayed_gratification import (
    get_category_spending_trends,
    detect_delayed_gratification,
    generate_delayed_gratification_insights,
    display_delayed_gratification_insights,
    classify_category
)

# Load test data
df = pd.read_csv('data/multi_month_transactions.csv')
df['date'] = pd.to_datetime(df['date'])

print("="*70)
print("DELAYED GRATIFICATION INSIGHTS - TEST SUITE")
print("="*70)

# Test 1: Category Classification
print("\n" + "="*70)
print("TEST 1: CATEGORY CLASSIFICATION")
print("="*70)
test_categories = ['Eating Out', 'Rent', 'Entertainment', 'Groceries', 'Shopping', 'Coffee']
for cat in test_categories:
    classification = classify_category(cat)
    print(f"{cat:20s} -> {classification}")

# Test 2: Category Spending Trends
print("\n" + "="*70)
print("TEST 2: CATEGORY SPENDING TRENDS (Stage 1)")
print("="*70)
trends = get_category_spending_trends(df)
if not trends.empty:
    print(trends.to_string(index=False))
else:
    print("No trends detected")

# Test 3: Delayed Gratification Detection
print("\n" + "="*70)
print("TEST 3: DELAYED GRATIFICATION DETECTION (Stage 2)")
print("="*70)
delayed_grat = detect_delayed_gratification(trends)
if not delayed_grat.empty:
    print(delayed_grat.to_string(index=False))
    print("\nDetailed Insights:")
    for idx, row in delayed_grat.iterrows():
        print(f"\n{row['insight']}")
else:
    print("No delayed gratification detected")

# Test 4: Full Insights Generation
print("\n" + "="*70)
print("TEST 4: FULL INSIGHTS GENERATION (All Stages)")
print("="*70)
display_delayed_gratification_insights(df)

print("\n" + "="*70)
print("TEST SUITE COMPLETE")
print("="*70)
