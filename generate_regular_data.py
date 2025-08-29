#!/usr/bin/env python3
"""
Generate regular, predictable business sales data sorted by time:
- Consistent weekly patterns
- Smooth monthly growth
- Minimal random noise
- Properly sorted by date
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

def generate_regular_sales_data():
    # Set random seed for reproducibility
    np.random.seed(42)
    
    # Generate date range for full year 2024 (sorted)
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2024, 12, 31)
    dates = pd.date_range(start=start_date, end=end_date, freq='D')
    
    # Base sales value
    base_sales = 1000
    
    # Initialize sales array
    sales = []
    
    for i, date in enumerate(dates):
        # 1. Linear growth trend (20% annual growth, very smooth)
        days_from_start = (date - start_date).days
        trend = base_sales + (200 * days_from_start / 365)  # Linear growth from 1000 to 1200
        
        # 2. Regular weekly pattern (very predictable)
        day_of_week = date.dayofweek
        weekly_pattern = {
            0: 1.0,   # Monday - normal
            1: 1.1,   # Tuesday - slightly higher
            2: 1.2,   # Wednesday - mid-week peak
            3: 1.15,  # Thursday - above average
            4: 1.05,  # Friday - slightly above normal
            5: 0.8,   # Saturday - weekend drop
            6: 0.7    # Sunday - lowest
        }
        dow_factor = weekly_pattern[day_of_week]
        
        # 3. Monthly seasonality (smooth sine wave)
        # Peak in summer (June-July), low in winter (Jan-Feb)
        day_of_year = date.timetuple().tm_yday
        seasonal_factor = 1.0 + 0.2 * np.sin(2 * np.pi * day_of_year / 365 - np.pi/2)
        
        # 4. Very small random noise (±2% only)
        noise = np.random.normal(1.0, 0.02)
        
        # Combine all factors
        daily_sales = trend * dow_factor * seasonal_factor * noise
        
        # Round to nearest 10 for cleaner numbers
        daily_sales = round(daily_sales / 10) * 10
        
        # Ensure non-negative
        daily_sales = max(0, daily_sales)
        
        sales.append(daily_sales)
    
    # Create DataFrame (already sorted by date)
    df = pd.DataFrame({
        'Date': dates.strftime('%Y-%m-%d'),
        'Value': sales
    })
    
    return df

def generate_detailed_regular_data():
    """Generate version with additional metadata"""
    df = generate_regular_sales_data()
    
    # Add metadata columns
    dates = pd.to_datetime(df['Date'])
    df['Day_of_Week'] = dates.dt.strftime('%A')
    df['Week_Number'] = dates.dt.isocalendar().week
    df['Month'] = dates.dt.strftime('%B')
    df['Quarter'] = ['Q' + str(d.quarter) for d in dates]
    df['Is_Weekend'] = dates.dt.dayofweek.isin([5, 6])
    
    return df

def save_regular_datasets():
    # Generate regular sales data
    df_simple = generate_regular_sales_data()
    df_detailed = generate_detailed_regular_data()
    
    # Save datasets
    output_dir = 'data'
    os.makedirs(output_dir, exist_ok=True)
    
    # Save simple version (Date, Value)
    df_simple.to_csv(f'{output_dir}/regular_sales.csv', index=False)
    print(f"Saved regular dataset: {output_dir}/regular_sales.csv")
    
    # Save detailed version
    df_detailed.to_csv(f'{output_dir}/regular_sales_detailed.csv', index=False)
    print(f"Saved detailed dataset: {output_dir}/regular_sales_detailed.csv")
    
    # Print summary statistics
    print("\n=== Regular Dataset Summary ===")
    print(f"Date range: {df_simple['Date'].min()} to {df_simple['Date'].max()}")
    print(f"Total days: {len(df_simple)}")
    print(f"Average daily sales: ${df_simple['Value'].mean():.2f}")
    print(f"Min sales: ${df_simple['Value'].min()}")
    print(f"Max sales: ${df_simple['Value'].max()}")
    print(f"Standard deviation: ${df_simple['Value'].std():.2f}")
    print(f"Total annual sales: ${df_simple['Value'].sum():,}")
    
    # Show sample of data (first week)
    print("\n=== First Week (showing regular weekly pattern) ===")
    print(df_detailed.head(7)[['Date', 'Value', 'Day_of_Week']].to_string(index=False))
    
    # Show mid-year sample
    print("\n=== Mid-Year Sample (July 1-7) ===")
    mid_year = df_detailed[df_detailed['Date'].str.startswith('2024-07-0')].head(7)
    print(mid_year[['Date', 'Value', 'Day_of_Week']].to_string(index=False))
    
    # Verify data is sorted
    dates_sorted = pd.to_datetime(df_simple['Date'])
    is_sorted = dates_sorted.is_monotonic_increasing
    print(f"\n✓ Data is sorted by date: {is_sorted}")
    
    # Show weekly pattern consistency
    print("\n=== Weekly Pattern (Average by Day of Week) ===")
    weekly_avg = df_detailed.groupby('Day_of_Week')['Value'].mean()
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    for day in days_order:
        print(f"{day:10s}: ${weekly_avg[day]:,.0f}")
    
    return df_simple, df_detailed

if __name__ == "__main__":
    df_simple, df_detailed = save_regular_datasets()
    print("\n✅ Regular, time-sorted sales data generated successfully!")
    print("The data has predictable patterns with minimal randomness.")