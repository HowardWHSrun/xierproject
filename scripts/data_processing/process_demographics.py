#!/usr/bin/env python3
"""
Process demographic data and link to TPU boundaries.
Handles TPU boundary changes across years.
"""

import pandas as pd
import geopandas as gpd
from pathlib import Path
import os
import json

def load_demographic_data(year: str, data_dir: Path = None) -> pd.DataFrame:
    """
    Load demographic data for a specific year.
    Supports CSV and Excel formats.
    """
    if data_dir is None:
        project_root = Path(__file__).parent.parent.parent
        data_dir = project_root / 'data' / 'raw' / 'demographics' / f'census_{year}'
    
    print(f"\nLoading {year} demographic data from {data_dir}...")
    
    if not data_dir.exists():
        print(f"  Directory not found: {data_dir}")
        print("  Please download demographic data first")
        return pd.DataFrame()
    
    # Look for data files (case-insensitive)
    data_files = []
    for ext in ['.csv', '.CSV', '.xlsx', '.XLSX', '.xls', '.XLS']:
        data_files.extend(list(data_dir.glob(f'*{ext}')))
    
    if not data_files:
        print(f"  No data files found in {data_dir}")
        return pd.DataFrame()
    
    # Try to load the first file found
    data_file = data_files[0]
    print(f"  Loading from: {data_file.name}")
    
    try:
        if data_file.suffix == '.csv':
            # Try different encodings for CSV files
            try:
                # For 2021 data, the CSV has 3 header rows:
                # Row 0: Chinese headers
                # Row 1: English headers  
                # Row 2: Short code headers (use this as column names)
                # Row 3+: Data
                df = pd.read_csv(data_file, encoding='utf-8', skiprows=2, header=0)
            except UnicodeDecodeError:
                try:
                    df = pd.read_csv(data_file, encoding='utf-8-sig', skiprows=2, header=0)
                except:
                    df = pd.read_csv(data_file, encoding='latin-1', skiprows=2, header=0)
            
            # Clean up: remove rows that are still headers or empty
            # Check if first row is actually a header row (contains 'Large Tertiary Planning Unit Group' or similar)
            if len(df) > 0:
                first_val = str(df.iloc[0, 0]).lower()
                if 'large tertiary' in first_val or 'small tertiary' in first_val or first_val == 'ltpug' or first_val == 'stpug':
                    df = df.iloc[1:].reset_index(drop=True)
        else:
            df = pd.read_excel(data_file)
        
        # Remove any remaining header-like rows
        if len(df) > 0:
            # Check if first column contains 'ltpug' or 'stpug' as a value (should be in column name, not data)
            first_col = df.columns[0]
            if df[first_col].dtype == 'object':
                mask = ~df[first_col].astype(str).str.lower().isin(['ltpug', 'stpug', 'large tertiary planning unit group', 'small tertiary planning unit group'])
                df = df[mask].reset_index(drop=True)
        
        print(f"  Loaded {len(df)} records with {len(df.columns)} columns")
        return df
        
    except Exception as e:
        print(f"  Error loading data: {e}")
        return pd.DataFrame()


def link_demographics_to_tpu(demographics_df: pd.DataFrame, tpu_gdf: gpd.GeoDataFrame, 
                              tpu_id_column: str = 'TPU_ID', year: str = None) -> gpd.GeoDataFrame:
    """
    Link demographic data to TPU boundaries.
    """
    if demographics_df.empty:
        return tpu_gdf
    
    # Try to identify TPU ID column in demographic data
    # For 2021 data, the column is 'ltpug' (Large Tertiary Planning Unit Group)
    # For other years, try common column names
    demo_tpu_col = None
    
    # Check for specific column names based on data format
    if 'ltpug' in demographics_df.columns:
        demo_tpu_col = 'ltpug'
    elif 'stpug' in demographics_df.columns:
        demo_tpu_col = 'stpug'
    else:
        # Try common column names
        for col in ['TPU_ID', 'TPU_CODE', 'CODE', 'ID', 'TPU', 'tpu_id', 'tpu_code', 
                   'Large Tertiary Planning Unit Group', 'Small Tertiary Planning Unit Group']:
            if col in demographics_df.columns:
                demo_tpu_col = col
                break
    
    if demo_tpu_col is None:
        print("  Warning: Could not identify TPU ID column in demographic data")
        print(f"  Available columns (first 10): {list(demographics_df.columns[:10])}")
        return tpu_gdf
    
    print(f"  Using TPU ID column: {demo_tpu_col}")
    
    # Convert TPU ID to string for matching (in case of type mismatch)
    demographics_df[demo_tpu_col] = demographics_df[demo_tpu_col].astype(str)
    tpu_gdf[tpu_id_column] = tpu_gdf[tpu_id_column].astype(str)
    
    # Merge demographic data with TPU boundaries
    merged = tpu_gdf.merge(
        demographics_df,
        left_on=tpu_id_column,
        right_on=demo_tpu_col,
        how='left'
    )
    
    matched_count = merged[demo_tpu_col].notna().sum()
    print(f"  Linked demographics to {matched_count} out of {len(tpu_gdf)} TPUs")
    
    return merged


def process_all_demographics():
    """
    Process demographic data for all available years.
    """
    project_root = Path(__file__).parent.parent.parent
    output_dir = project_root / 'data' / 'processed' / 'demographics'
    os.makedirs(output_dir, exist_ok=True)
    
    years = ['2001', '2006', '2011', '2016', '2021']
    
    print("=" * 60)
    print("Processing Demographic Data")
    print("=" * 60)
    
    for year in years:
        # Load TPU boundaries
        tpu_file = project_root / 'data' / 'processed' / 'tpu' / f'tpu_boundaries_{year}_processed.geojson'
        
        if not tpu_file.exists():
            print(f"\n{year}: TPU boundaries not found, skipping...")
            continue
        
        tpu_gdf = gpd.read_file(tpu_file)
        
        # Load demographic data
        demo_df = load_demographic_data(year)
        
        if demo_df.empty:
            print(f"{year}: No demographic data available")
            # Save TPU boundaries without demographics for now
            output_file = output_dir / f'tpu_demographics_{year}.geojson'
            tpu_gdf.to_file(output_file, driver='GeoJSON')
            print(f"  Saved TPU boundaries (without demographics) to {output_file}")
            continue
        
        # Link demographics to TPUs
        merged_gdf = link_demographics_to_tpu(demo_df, tpu_gdf, year=year)
        
        # Save processed data
        output_file = output_dir / f'tpu_demographics_{year}.geojson'
        merged_gdf.to_file(output_file, driver='GeoJSON')
        
        # Also save as CSV for easier analysis
        csv_file = output_dir / f'tpu_demographics_{year}.csv'
        # Drop geometry for CSV
        merged_gdf.drop(columns=['geometry']).to_csv(csv_file, index=False)
        
        print(f"  Saved to {output_file} and {csv_file}")
    
    print("\n" + "=" * 60)
    print("Processing complete!")
    print("=" * 60)


if __name__ == '__main__':
    process_all_demographics()

