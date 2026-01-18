# Personal Finance Analyzer

Personal Finance Analyzer is a Python-based command-line tool that converts raw transaction CSVs into actionable financial insights and scenario-based projections. It helps users understand cash flow, test savings goals, and stress-test finances under income or expense changes.

## Project Overview

What problem it solves
- Many people can export transaction CSVs but lack tools to answer forward-looking questions such as:
  - How long could I survive without income?
  - What happens if my expenses increase?
  - Is my savings goal achievable under different scenarios?
  - How sensitive are my finances to income or spending changes?
- This tool transforms historical transactions into structured insights: monthly cash flow, savings trends, emergency fund runway, and goal feasibility under alternative scenarios.

Who is it for
- Individuals seeking a clearer, data-driven view of their finances (easy to present to stakeholders such as family)
- Students and early-career professionals planning budgets and savings goals
- Data and finance learners applying Python and pandas to real-world data

## Features

Load and Validate Transactions

- Imports transaction data from a CSV file.
- Automatically handles common CSV formatting issues, such as different delimiters and encodings (flexible CSV parsing and column mapping)
- Validates and standardizes required columns: date, category, and amount.
- Provides a sample CSV file if no data file is provided.

After loading data, the user is prompted into choosing from tools: 

1. Monthly Cash Flow Summary

- Groups transactions by month.
- Calculates total income, total expenses, and net cash flow per month.
- Provides a clean, easy-to-read monthly summary.

2. Total Savings Calculation

- Computes total savings based on the cumulative net cash flow.
- Assumes savings accumulate from positive net cash flow over time.

3. Emergency Fund Runway
- Estimates how many months you could sustain your lifestyle using current savings without any additional income.
- Uses average monthly expenses to determine the runway as savings/ average monthly expenses

4. Scenario Projection & Analysis

- Allows “what-if” scenarios to see how changes in income or expenses affect future savings.
- Projects cumulative savings over a user-specified number of months.
- Checks the achievability of a savings goal within a target date.
- Integrates required monthly savings as an additional expense for goal planning.

5. Category Spending Breakdown

- Summarizes spending by category.
- Shows the total amount spent per category and the percentage of total expenses.
- Helps identify areas where money could be saved.

After required output, different tool can be selected from the prompt. 


## How to Run

### Install
1. Clone repository and enter project directory:
```bash
git clone https://github.com/yourusername/SK-Personal-finance-portfolio.git
cd SK-Personal-finance-portfolio
```
2. (Optional) Create and activate a virtual environment:
```bash
python3 -m venv .venv
source .venv/bin/activate
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```

### Run
```bash
python src/cashflow.py
```
When prompted, press Enter to use the default sample (`data/sample_transactions.csv`) or provide a path to your CSV file.

Input example (CSV):
```csv
date,category,amount
2025-06-01,Salary,1200.00
2025-06-02,Food,-42.50
2025-06-05,Rent,-600.00
```
Select required tool from a range of options

### Typical workflow
- Choose a file when prompted (or press Enter for sample data)
- Use the interactive menu to view monthly summaries, check total savings, compute emergency runway, run scenario projections, or view category spending breakdowns

## Assumptions & Limitations
- Requires CSV input with at least the columns: `date`, `category`, `amount` (column names are case-insensitive and aliases are supported).
- Dates are parsed with common formats; ambiguous formats may require pre-normalization.
- Amounts: positive values denote income; negative values denote expenses.
- Projections are simple deterministic scenarios (additive changes per month); they don't model uncertain income, taxes, or complex investment returns.
- Not financial advice. Use results as illustrative guidance, not a substitute for professional planning.

## License
- MIT License
