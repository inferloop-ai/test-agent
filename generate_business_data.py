#!/usr/bin/env python3
"""
Generate realistic business sales data with patterns:
- Overall upward trend
- Weekly patterns (lower on weekends)
- Monthly seasonality (higher at month-end)
- Quarterly patterns (higher in Q4)
- Random noise for realism
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_business_sales_data():
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # Generate date range for full year 2024
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Base sales value
    base_sales = 1000
    
    # Initialize sales array
    sales = np.zeros(len(dates))
    
    for i, date in enumerate(dates):
        # 1. Overall growth trend (15% annual growth)
        days_from_start = (date - start_date).days
        trend = base_sales * (1 + 0.15 * days_from_start / 365)
        
        # 2. Day of week pattern (lower on weekends)
        day_of_week = date.dayofweek
        if day_of_week == 5:  # Saturday
            dow_factor = 0.7
        elif day_of_week == 6:  # Sunday
            dow_factor = 0.6
        else:  # Weekdays
            dow_factor = 1.0 + 0.1 * (4 - abs(day_of_week - 2))  # Peak on Wednesday
        
        # 3. Monthly pattern (higher at month-end)
        day_of_month = date.day
        days_in_month = pd.Timestamp(date).days_in_month
        if day_of_month >= days_in_month - 3:  # Last 3 days of month
            month_factor = 1.3
        elif day_of_month <= 5:  # First 5 days
            month_factor = 0.9
        else:
            month_factor = 1.0
        
        # 4. Quarterly pattern (Q4 holiday season boost)
        quarter = date.quarter
        if quarter == 4:  # Q4 - holiday season
            quarter_factor = 1.25
        elif quarter == 1:  # Q1 - post-holiday slump
            quarter_factor = 0.85
        else:  # Q2 and Q3
            quarter_factor = 1.0
        
        # 5. Special events/holidays
        special_factor = 1.0
        # Black Friday (day after Thanksgiving - approximate)
        if date.month == 11 and 23 <= date.day <= 25:
            special_factor = 2.5
        # Cyber Monday
        elif date.month == 11 and 26 <= date.day <= 28:
            special_factor = 2.0
        # Christmas shopping season
        elif date.month == 12 and 15 <= date.day <= 24:
            special_factor = 1.5
        # Valentine's Day
        elif date.month == 2 and 12 <= date.day <= 14:
            special_factor = 1.3
        
        # 6. Random noise (±10%)
        noise = np.random.normal(1.0, 0.1)
        
        # Combine all factors
        sales[i] = trend * dow_factor * month_factor * quarter_factor * special_factor * noise
        
        # Ensure non-negative
        sales[i] = max(0, sales[i])
    
    # Round to integers
    sales = np.round(sales).astype(int)
    
    # Create DataFrame
    df = pd.DataFrame({
        'Date': dates.strftime('%Y-%m-%d'),
        'Sales': sales,
        'Day_of_Week': dates.strftime('%A'),
        'Month': dates.strftime('%B'),
        'Quarter': ['Q' + str(d.quarter) for d in dates]
    })
    
    return df

def save_datasets():
    # Generate main sales data
    df = generate_business_sales_data()
    
    # Save full dataset with metadata
    output_dir = 'data'
    os.makedirs(output_dir, exist_ok=True)
    
    # Save detailed version
    df.to_csv(f'{output_dir}/business_sales_detailed.csv', index=False)
    print(f"Saved detailed dataset: {output_dir}/business_sales_detailed.csv")
    
    # Save simple version (compatible with existing tools)
    df_simple = df[['Date', 'Sales']].copy()
    df_simple.rename(columns={'Sales': 'Value'}, inplace=True)
    df_simple.to_csv(f'{output_dir}/business_sales.csv', index=False)
    print(f"Saved simple dataset: {output_dir}/business_sales.csv")
    
    # Print summary statistics
    print("\n=== Dataset Summary ===")
    print(f"Date range: {df['Date'].min()} to {df['Date'].max()}")
    print(f"Total days: {len(df)}")
    print(f"Average daily sales: ${df['Sales'].mean():.2f}")
    print(f"Min sales: ${df['Sales'].min()}")
    print(f"Max sales: ${df['Sales'].max()}")
    print(f"Total annual sales: ${df['Sales'].sum():,}")
    
    # Show sample of data
    print("\n=== First 10 days ===")
    print(df.head(10).to_string(index=False))
    
    print("\n=== Peak sales days ===")
    print(df.nlargest(5, 'Sales')[['Date', 'Sales', 'Day_of_Week']].to_string(index=False))
    
    return df

if __name__ == "__main__":
    df = save_datasets()
    print("\n✅ Business sales data generated successfully!")