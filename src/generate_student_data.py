import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Function to generate synthetic student cash flow data
def generate_student_data():
    # Define date range: 4 years of university (2021-2025)
    start_date = datetime(2021, 9, 1)
    end_date = datetime(2025, 6, 30)
    
    # Generate dates: weekly transactions for larger dataset
    dates = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date)
        current_date += timedelta(days=7)  # Weekly
    
    # Categories and typical amounts (positive for income, negative for expenses)
    income_categories = {
        'Part-time Job': (200, 500),  # Weekly pay
        'Scholarship': (0, 1000),     # Occasional lump sums
        'Allowance': (50, 200)        # Monthly
    }
    
    expense_categories = {
        'Rent': (400, 600),           # Monthly
        'Food': (50, 150),            # Weekly
        'Tuition': (1000, 2000),      # Semester
        'Books': (50, 200),           # Occasional
        'Entertainment': (20, 100),   # Weekly
        'Utilities': (30, 80),        # Monthly
        'Transportation': (20, 100),  # Weekly
        'Clothing': (50, 200)         # Occasional
    }
    
    transactions = []
    
    for date in dates:
        # Add income transactions (less frequent)
        if random.random() < 0.3:  # 30% chance of income per week
            category = random.choice(list(income_categories.keys()))
            amount = random.uniform(*income_categories[category])
            transactions.append({'date': date, 'category': category, 'amount': round(amount, 2)})
        
        # Add expense transactions (more frequent)
        if random.random() < 0.7:  # 70% chance of expense per week
            category = random.choice(list(expense_categories.keys()))
            amount = -random.uniform(*expense_categories[category])  # Negative for expenses
            transactions.append({'date': date, 'category': category, 'amount': round(amount, 2)})
    
    # Create DataFrame
    df = pd.DataFrame(transactions)
    
    # Sort by date
    df = df.sort_values('date').reset_index(drop=True)
    
    return df

# Generate the data
student_df = generate_student_data()

# Save to CSV
output_path = '../data/student_transactions.csv'
student_df.to_csv(output_path, index=False)

print(f"Generated {len(student_df)} transactions.")
print(f"Saved to {output_path}")
print("Sample data:")
print(student_df.head(10))