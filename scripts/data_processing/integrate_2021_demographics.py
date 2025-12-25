#!/usr/bin/env python3
"""
Integrate 2021 demographic data with 2016 TPU boundaries.
Since 2021 uses Large TPU Groups and 2016 uses individual TPUs,
we'll aggregate 2016 TPUs to match Large TPU groups.
"""

import pandas as pd
import geopandas as gpd
from pathlib import Path

def integrate_2021_demographics():
    """
    Integrate 2021 demographic data with 2016 TPU boundaries.
    """
    project_root = Path(__file__).parent.parent.parent
    
    print("=" * 60)
    print("Integrating 2021 Demographics with 2016 TPU Boundaries")
    print("=" * 60)
    
    # Load 2021 demographic data
    demo_2021_file = project_root / 'data' / 'processed' / 'demographics' / 'demographics_2021_raw.csv'
    demo_2021 = pd.read_csv(demo_2021_file)
    
    # Remove header row if present
    if str(demo_2021.iloc[0, 0]).lower() in ['ltpug', 'large tertiary planning unit group']:
        demo_2021 = demo_2021.iloc[1:].reset_index(drop=True)
    
    print(f"\n2021 Demographic Data:")
    print(f"  Records: {len(demo_2021)}")
    print(f"  TPU ID column: {demo_2021.columns[0]}")
    
    # Load 2016 TPU boundaries
    tpu_2016_file = project_root / 'data' / 'processed' / 'tpu' / 'tpu_boundaries_2016_processed.geojson'
    tpu_2016 = gpd.read_file(tpu_2016_file)
    
    print(f"\n2016 TPU Boundaries:")
    print(f"  TPUs: {len(tpu_2016)}")
    print(f"  Sample TPU IDs: {tpu_2016['TPU_ID'].head().tolist()}")
    
    # The 2021 data uses Large TPU Group codes (e.g., '111', '112L')
    # The 2016 TPU boundaries use individual TPU codes (e.g., '920', '911')
    # We need to match them. Large TPU groups are typically the first 3 digits
    # of individual TPU codes, or we can use a lookup table.
    
    # For now, let's create a simplified version where we:
    # 1. Extract the Large TPU Group code from 2021 data
    # 2. Try to match with 2016 TPU codes (first 3 digits)
    
    demo_2021_tpu_col = demo_2021.columns[0]  # First column is TPU ID
    demo_2021['LTPU_Code'] = demo_2021[demo_2021_tpu_col].astype(str).str.strip()
    
    # Remove 'L' suffix if present and normalize
    demo_2021['LTPU_Code_Clean'] = demo_2021['LTPU_Code'].str.replace('L', '', regex=False)
    
    # For 2016 TPUs, extract first 3 digits as potential Large TPU Group
    tpu_2016['LTPU_Prefix'] = tpu_2016['TPU_ID'].astype(str).str[:3]
    
    # Merge: match 2016 TPUs to 2021 Large TPU Groups
    # This is approximate - in reality, you'd need a proper lookup table
    tpu_2016_with_demo = tpu_2016.merge(
        demo_2021,
        left_on='LTPU_Prefix',
        right_on='LTPU_Code_Clean',
        how='left',
        suffixes=('', '_demo')
    )
    
    matched_count = tpu_2016_with_demo['LTPU_Code'].notna().sum()
    print(f"\nMatching Results:")
    print(f"  TPUs matched to 2021 demographics: {matched_count} out of {len(tpu_2016)}")
    print(f"  Match rate: {matched_count/len(tpu_2016)*100:.1f}%")
    
    # Save integrated data
    output_dir = project_root / 'data' / 'processed' / 'demographics'
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_file = output_dir / 'tpu_demographics_2016_with_2021.geojson'
    tpu_2016_with_demo.to_file(output_file, driver='GeoJSON')
    
    csv_file = output_dir / 'tpu_demographics_2016_with_2021.csv'
    tpu_2016_with_demo.drop(columns=['geometry']).to_csv(csv_file, index=False)
    
    print(f"\nSaved integrated data:")
    print(f"  GeoJSON: {output_file}")
    print(f"  CSV: {csv_file}")
    
    # Show sample of matched data
    if matched_count > 0:
        print(f"\nSample matched records:")
        sample_cols = ['TPU_ID', 'LTPU_Code', 't_pop'] if 't_pop' in tpu_2016_with_demo.columns else ['TPU_ID', 'LTPU_Code']
        print(tpu_2016_with_demo[tpu_2016_with_demo['LTPU_Code'].notna()][sample_cols].head())
    
    print("\n" + "=" * 60)
    print("Integration complete!")
    print("=" * 60)
    
    return tpu_2016_with_demo

if __name__ == '__main__':
    integrate_2021_demographics()

