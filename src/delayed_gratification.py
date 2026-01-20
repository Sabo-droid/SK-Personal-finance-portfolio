"""
Delayed Gratification Insights Module

This module detects, quantifies, and rewards delayed gratification behavior by:
1. Analyzing category spending trends month-over-month
2. Detecting reductions in discretionary spending
3. Projecting future value and mapping to meaningful outcomes
"""

import pandas as pd
from datetime import datetime

# Category classifications
DISCRETIONARY_CATEGORIES = {
    'eating out', 'entertainment', 'shopping', 'coffee', 'movies', 'dining', 
    'restaurants', 'subscriptions', 'gaming', 'hobbies', 'travel', 'vacation',
    'streaming', 'online shopping', 'clothes', 'fashion', 'alcohol', 'drinks',
    'social', 'hangout', 'leisure', 'recreation', 'games', 'books', 'music'
}

ESSENTIAL_CATEGORIES = {
    'rent', 'utilities', 'groceries', 'food', 'transportation', 'gas',
    'insurance', 'phone', 'internet', 'salary', 'income', 'wages',
    'scholarship', 'allowance', 'part-time job', 'work', 'healthcare',
    'medication', 'fitness', 'gym', 'tuition', 'education', 'school'
}

# Reward mapping: $ value ranges to student-relevant outcomes
REWARD_MAPPING = [
    (3000, "🎯 3 months of rent or a new Mac Pro!"),
    (1500, "✈️ A July flight to LAX"),
    (800, "🥋 One year sports fees"),
    (500, "📚 Course materials & textbooks for semester"),
    (300, "🎧 Apple Airpods Pro"),
    (150, "🍱 Weekly meals out for a month"),
    (75, "👚 Wardrobe upgrade"),
    (0, "💪 Every $1 counts toward your future")
]

MINIMUM_REDUCTION_THRESHOLD = 20  # dollars
MINIMUM_REDUCTION_PERCENT = 10  # percent


def classify_category(category_name):
    """
    Classify a category as discretionary, essential, or unknown.
    
    Args:
        category_name: String category name
    
    Returns:
        'discretionary', 'essential', or 'unknown'
    """
    category_lower = category_name.lower().strip()
    
    if category_lower in DISCRETIONARY_CATEGORIES:
        return 'discretionary'
    elif category_lower in ESSENTIAL_CATEGORIES:
        return 'essential'
    else:
        # Try substring matching
        for disc_cat in DISCRETIONARY_CATEGORIES:
            if disc_cat in category_lower or category_lower in disc_cat:
                return 'discretionary'
        for ess_cat in ESSENTIAL_CATEGORIES:
            if ess_cat in category_lower or category_lower in ess_cat:
                return 'essential'
    
    return 'unknown'


def get_category_spending_trends(df):
    """
    Stage 1: Calculate category spending trends month-over-month.
    
    Args:
        df: DataFrame with 'date', 'category', 'amount' columns
    
    Returns:
        DataFrame with columns:
        - category
        - previous_month
        - current_month
        - previous_month_spend
        - current_month_spend
        - absolute_change
        - percentage_change
        - trend_direction
        - classification
    """
    # Create month column
    df_copy = df.copy()
    df_copy['month'] = df_copy['date'].dt.to_period('M')
    
    # Filter only expenses (negative amounts)
    expenses_df = df_copy[df_copy['amount'] < 0].copy()
    expenses_df['amount'] = -expenses_df['amount']  # Make positive for easier analysis
    
    if expenses_df.empty:
        return pd.DataFrame()
    
    # Group by category and month
    category_monthly = expenses_df.groupby(['category', 'month'])['amount'].sum().reset_index()
    
    # Get unique months sorted
    months = sorted(category_monthly['month'].unique())
    
    if len(months) < 2:
        # Not enough data for trend analysis
        return pd.DataFrame()
    
    trends = []
    
    # For each category, calculate month-over-month changes
    for category in category_monthly['category'].unique():
        category_data = category_monthly[category_monthly['category'] == category].sort_values('month')
        
        # Only analyze if we have at least 2 months of data
        if len(category_data) >= 2:
            # Get previous and current month (last two months)
            prev_month_row = category_data.iloc[-2]
            curr_month_row = category_data.iloc[-1]
            
            prev_spend = prev_month_row['amount']
            curr_spend = curr_month_row['amount']
            
            absolute_change = curr_spend - prev_spend
            percentage_change = (absolute_change / prev_spend * 100) if prev_spend > 0 else 0
            
            # Determine trend direction
            if absolute_change > 0:
                trend_direction = 'increase'
            elif absolute_change < 0:
                trend_direction = 'decrease'
            else:
                trend_direction = 'stable'
            
            classification = classify_category(category)
            
            trends.append({
                'category': category,
                'previous_month': str(prev_month_row['month']),
                'current_month': str(curr_month_row['month']),
                'previous_month_spend': prev_spend,
                'current_month_spend': curr_spend,
                'absolute_change': absolute_change,
                'percentage_change': percentage_change,
                'trend_direction': trend_direction,
                'classification': classification
            })
    
    return pd.DataFrame(trends)


def detect_delayed_gratification(df):
    """
    Stage 2: Detect delayed gratification behavior.
    
    A category qualifies if:
    - It's discretionary
    - Spending decreased month-over-month
    - Reduction exceeds minimum threshold ($20 or 10%)
    
    Args:
        df: Trends DataFrame from get_category_spending_trends()
    
    Returns:
        DataFrame with detected delayed gratification instances
    """
    if df.empty:
        return pd.DataFrame()
    
    # Filter for discretionary categories with decreasing spending
    delayed_grat = df[
        (df['classification'] == 'discretionary') & 
        (df['trend_direction'] == 'decrease')
    ].copy()
    
    if delayed_grat.empty:
        return pd.DataFrame()
    
    # Filter by minimum thresholds
    delayed_grat['meets_threshold'] = (
        (delayed_grat['absolute_change'].abs() >= MINIMUM_REDUCTION_THRESHOLD) |
        (delayed_grat['percentage_change'].abs() >= MINIMUM_REDUCTION_PERCENT)
    )
    
    delayed_grat = delayed_grat[delayed_grat['meets_threshold']].copy()
    
    if delayed_grat.empty:
        return pd.DataFrame()
    
    # Add saved amount (positive value)
    delayed_grat['saved_amount'] = -delayed_grat['absolute_change']
    
    # Add behavioral insight
    delayed_grat['insight'] = delayed_grat.apply(
        lambda row: f"You chose not to spend ${row['saved_amount']:.2f} on {row['category'].title()} this month.\n"
                    f"This reflects a {abs(row['percentage_change']):.0f}% reduction compared to last month.",
        axis=1
    )
    
    return delayed_grat[['category', 'previous_month_spend', 'current_month_spend', 
                         'saved_amount', 'percentage_change', 'insight']]


def project_future_value(saved_amount, horizons=[6, 24, 60]):
    """
    Project future value of saved amount at different time horizons.
    
    Args:
        saved_amount: Amount saved in current month
        horizons: List of months to project (default: 6, 24, 60 months)
    
    Returns:
        List of dicts with projected values
    """
    projections = []
    
    for months in horizons:
        future_value = saved_amount * months
        projections.append({
            'months': months,
            'future_value': future_value
        })
    
    return projections


def map_to_reward(future_value):
    """
    Map future value to meaningful student-relevant reward.
    
    Args:
        future_value: Projected future value in dollars
    
    Returns:
        Reward description string
    """
    for threshold, description in REWARD_MAPPING:
        if future_value >= threshold:
            return description
    
    return REWARD_MAPPING[-1][1]  # Default message


def generate_delayed_gratification_insights(df):
    """
    Main entry point: Generate comprehensive delayed gratification insights.
    
    Args:
        df: Original transaction DataFrame with 'date', 'category', 'amount'
    
    Returns:
        Dict containing:
        - trends: DataFrame of category trends
        - delayed_gratification: DataFrame of detected instances
        - detailed_insights: List of formatted insight strings
        - summary: Aggregated insight message
    """
    # Stage 1: Calculate trends
    trends = get_category_spending_trends(df)
    
    if trends.empty:
        return {
            'trends': pd.DataFrame(),
            'delayed_gratification': pd.DataFrame(),
            'detailed_insights': [],
            'summary': "Not enough historical data to detect spending patterns. Check back next month!"
        }
    
    # Stage 2: Detect delayed gratification
    delayed_grat = detect_delayed_gratification(trends)
    
    if delayed_grat.empty:
        return {
            'trends': trends,
            'delayed_gratification': pd.DataFrame(),
            'detailed_insights': [],
            'summary': "No significant spending reductions detected this month. Keep building your habits!"
        }
    
    # Stage 3: Generate detailed insights with future value projections
    detailed_insights = []
    total_saved = 0
    
    for idx, row in delayed_grat.iterrows():
        category = row['category']
        saved_amount = row['saved_amount']
        insight_text = row['insight']
        
        total_saved += saved_amount
        
        # Project future values
        projections = project_future_value(saved_amount)
        
        # Build detailed insight
        insight_block = f"\n{'='*60}\n"
        insight_block += f"DELAYED GRATIFICATION INSIGHT: {category.upper()}\n"
        insight_block += f"{'='*60}\n\n"
        insight_block += f"{insight_text}\n\n"
        
        insight_block += "If this behavior continues:\n"
        for proj in projections:
            months = proj['months']
            future_val = proj['future_value']
            reward = map_to_reward(future_val)
            
            # Format months nicely
            if months == 6:
                time_frame = "In 6 months"
            elif months == 24:
                time_frame = "In 2 years"
            elif months == 60:
                time_frame = "In 5 years"
            else:
                time_frame = f"In {months} months"
            
            insight_block += f"  {time_frame}: ~${future_val:,.2f}\n"
        
        # Add top reward
        top_reward = map_to_reward(projections[0]['future_value'])
        insight_block += f"\nThis could fund:\n  {top_reward}\n"
        
        detailed_insights.append(insight_block)
    
    # Generate summary
    summary = f"\n{'='*60}\n"
    summary += f"MONTHLY DELAYED GRATIFICATION SUMMARY\n"
    summary += f"{'='*60}\n\n"
    summary += f"✨ This month, you intentionally avoided ${total_saved:,.2f} in discretionary spending.\n"
    
    # Calculate percentage increase in savings rate (rough estimate)
    # Compare avoided spending to total expenses
    total_expenses = df[df['amount'] < 0]['amount'].sum()
    total_expenses = -total_expenses
    
    if total_expenses > 0:
        savings_rate_impact = (total_saved / total_expenses) * 100
        summary += f"💪 That's a {savings_rate_impact:.1f}% reduction in your spending.\n"
    
    summary += f"\n🎯 You traded short-term pleasure for long-term flexibility.\n"
    summary += f"💡 Keep it up! Consistency builds wealth.\n"
    
    return {
        'trends': trends,
        'delayed_gratification': delayed_grat,
        'detailed_insights': detailed_insights,
        'summary': summary
    }


def display_delayed_gratification_insights(df):
    """
    Pretty-print delayed gratification insights to console.
    
    Args:
        df: Transaction DataFrame
    """
    insights = generate_delayed_gratification_insights(df)
    
    # Print header
    print("\n" + "="*60)
    print("     DELAYED GRATIFICATION INSIGHTS")
    print("="*60)
    
    # Print detailed insights
    if insights['detailed_insights']:
        for insight_block in insights['detailed_insights']:
            print(insight_block)
    else:
        print("\nNo delayed gratification detected. That's okay - keep working on your goals!")
    
    # Print summary
    print(insights['summary'])
    print()
