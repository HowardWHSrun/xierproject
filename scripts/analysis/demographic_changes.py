#!/usr/bin/env python3
"""
Track demographic changes over time and correlate with MTR proximity.
"""

import pandas as pd
import numpy as np
from pathlib import Path
import os

def load_demographic_data_by_year() -> dict:
    """
    Load demographic data for each year.
    """
    project_root = Path(__file__).parent.parent.parent
    years = ['2001', '2006', '2011', '2016']
    
    demographic_data = {}
    
    for year in years:
        # Try processed demographics first
        demo_file = project_root / 'data' / 'processed' / 'demographics' / f'tpu_demographics_{year}.csv'
        
        if demo_file.exists():
            df = pd.read_csv(demo_file)
            demographic_data[year] = df
            print(f"Loaded {year} demographic data: {len(df)} TPUs")
        else:
            print(f"{year} demographic data not found")
    
    return demographic_data


def calculate_demographic_changes(demographic_data: dict) -> pd.DataFrame:
    """
    Calculate demographic changes between years.
    """
    if len(demographic_data) < 2:
        print("Need at least 2 years of data to calculate changes")
        return pd.DataFrame()
    
    years = sorted(demographic_data.keys())
    all_changes = []
    
    for i in range(len(years) - 1):
        year1 = years[i]
        year2 = years[i + 1]
        
        df1 = demographic_data[year1]
        df2 = demographic_data[year2]
        
        # Merge on TPU_ID
        merged = df1.merge(df2, on='TPU_ID', suffixes=(f'_{year1}', f'_{year2}'))
        
        # Find demographic columns
        demo_cols = [col for col in merged.columns 
                    if col not in ['TPU_ID', 'YEAR', 'geometry'] and 
                    not col.endswith(f'_{year1}') and not col.endswith(f'_{year2}')]
        
        # Calculate changes for each demographic variable
        for col in demo_cols:
            col1 = f'{col}_{year1}'
            col2 = f'{col}_{year2}'
            
            if col1 in merged.columns and col2 in merged.columns:
                merged[f'{col}_change'] = merged[col2] - merged[col1]
                merged[f'{col}_change_pct'] = ((merged[col2] - merged[col1]) / merged[col1] * 100).fillna(0)
        
        # Add year information
        merged['period'] = f'{year1}-{year2}'
        all_changes.append(merged)
    
    if all_changes:
        return pd.concat(all_changes, ignore_index=True)
    
    return pd.DataFrame()


def correlate_changes_with_mtr(demographic_changes: pd.DataFrame) -> pd.DataFrame:
    """
    Correlate demographic changes with MTR proximity.
    """
    project_root = Path(__file__).parent.parent.parent
    
    # Load spatial join data
    spatial_file = project_root / 'data' / 'analysis' / 'mtr_tpu_spatial_join_all_years.csv'
    
    if not spatial_file.exists():
        print("Spatial join data not found")
        return pd.DataFrame()
    
    spatial_data = pd.read_csv(spatial_file)
    
    # Merge demographic changes with MTR proximity
    merged = demographic_changes.merge(
        spatial_data[['TPU_ID', 'year', 'nearest_mtr_distance', 'has_mtr_station', 
                     'within_1000m_buffer', 'mtr_proximity_category']],
        on=['TPU_ID', 'year'],
        how='left'
    )
    
    return merged


def demographic_changes_analysis():
    """
    Main function to analyze demographic changes.
    """
    project_root = Path(__file__).parent.parent.parent
    
    print("=" * 60)
    print("Demographic Changes Analysis")
    print("=" * 60)
    
    # Load demographic data
    demo_data = load_demographic_data_by_year()
    
    if not demo_data:
        print("\nNo demographic data available yet.")
        print("This analysis will run once demographic data is integrated.")
        print("\nTo integrate demographic data:")
        print("1. Download data to data/raw/demographics/census_{YEAR}/")
        print("2. Run: python scripts/data_processing/process_demographics.py")
        return
    
    # Calculate changes
    print("\nCalculating demographic changes...")
    changes = calculate_demographic_changes(demo_data)
    
    if changes.empty:
        print("Could not calculate changes")
        return
    
    # Correlate with MTR
    print("Correlating changes with MTR proximity...")
    mtr_correlated = correlate_changes_with_mtr(changes)
    
    # Save results
    output_file = project_root / 'data' / 'analysis' / 'demographic_changes.csv'
    mtr_correlated.to_csv(output_file, index=False)
    
    print(f"\nSaved results to {output_file}")
    print(f"Total change observations: {len(mtr_correlated)}")
    
    # Summary statistics
    if 'nearest_mtr_distance' in mtr_correlated.columns:
        print("\nSummary by MTR Proximity:")
        print(mtr_correlated.groupby('mtr_proximity_category').agg({
            'nearest_mtr_distance': 'mean'
        }))
    
    print("\n" + "=" * 60)
    print("Demographic changes analysis complete!")
    print("=" * 60)


if __name__ == '__main__':
    demographic_changes_analysis()

