#!/usr/bin/env python3
"""
Temporal analysis: Compare demographics before vs. after MTR station openings.
"""

import pandas as pd
import geopandas as gpd
from pathlib import Path
import os
from datetime import datetime

def load_mtr_opening_dates() -> pd.DataFrame:
    """
    Load or create MTR station opening dates.
    Note: This would ideally come from MTR historical data.
    For now, we'll use approximate dates based on line openings.
    """
    project_root = Path(__file__).parent.parent.parent
    
    # Try to load from file if it exists
    mtr_dates_file = project_root / 'data' / 'raw' / 'mtr' / 'mtr_opening_dates.csv'
    
    if mtr_dates_file.exists():
        return pd.read_csv(mtr_dates_file)
    
    # Create approximate opening dates based on line history
    # This is a placeholder - actual dates should be researched
    mtr_stations_file = project_root / 'data' / 'raw' / 'mtr' / 'mtr_stations.xlsx'
    
    if mtr_stations_file.exists():
        df = pd.read_excel(mtr_stations_file)
        
        # Create approximate opening dates (placeholder logic)
        # In reality, these should be researched from MTR history
        opening_dates = []
        for idx, station in df.iterrows():
            station_name = station.get('Station Name (English)', '')
            lines = str(station.get('Lines', ''))
            
            # Approximate opening dates based on line (placeholder)
            # These are rough estimates and should be replaced with actual data
            if 'Island' in lines or 'Tsuen Wan' in lines:
                opening_date = '1979-10-01'  # Original MTR lines
            elif 'Kwun Tong' in lines:
                opening_date = '1979-10-01'
            elif 'Tseung Kwan O' in lines:
                opening_date = '2002-08-18'
            elif 'Tung Chung' in lines or 'Airport Express' in lines:
                opening_date = '1998-06-22'
            elif 'Disneyland' in lines:
                opening_date = '2005-08-01'
            elif 'West Rail' in lines or 'Tuen Ma' in lines:
                opening_date = '2003-12-20'
            elif 'East Rail' in lines:
                opening_date = '1910-10-01'  # Original KCR
            elif 'South Island' in lines:
                opening_date = '2016-12-28'
            else:
                opening_date = '2000-01-01'  # Default placeholder
            
            opening_dates.append({
                'Station Name (English)': station_name,
                'Opening Date': opening_date,
                'Opening Year': int(opening_date.split('-')[0])
            })
        
        dates_df = pd.DataFrame(opening_dates)
        
        # Save for future use
        os.makedirs(mtr_dates_file.parent, exist_ok=True)
        dates_df.to_csv(mtr_dates_file, index=False)
        
        return dates_df
    
    return pd.DataFrame()


def identify_affected_tpus(station_name: str, opening_year: int, 
                          spatial_join_data: pd.DataFrame) -> pd.DataFrame:
    """
    Identify TPUs affected by a station opening.
    """
    # Filter TPUs within 1000m of the station (walking distance)
    affected = spatial_join_data[
        (spatial_join_data['nearest_mtr_station'] == station_name) &
        (spatial_join_data['nearest_mtr_distance'] <= 1000) &
        (spatial_join_data['year'].astype(int) >= opening_year)
    ].copy()
    
    return affected


def compare_before_after(opening_year: int, spatial_join_data: pd.DataFrame,
                         demographic_data: pd.DataFrame = None) -> pd.DataFrame:
    """
    Compare demographics before and after MTR station openings.
    """
    print(f"\nAnalyzing before/after effects for stations opening in {opening_year}...")
    
    # Get MTR opening dates
    mtr_dates = load_mtr_opening_dates()
    
    if mtr_dates.empty:
        print("  No MTR opening dates available")
        return pd.DataFrame()
    
    # Filter stations opening in this year
    stations_opening = mtr_dates[mtr_dates['Opening Year'] == opening_year]
    
    if len(stations_opening) == 0:
        print(f"  No stations opened in {opening_year}")
        return pd.DataFrame()
    
    print(f"  Found {len(stations_opening)} stations opening in {opening_year}")
    
    # For each station, identify affected TPUs
    results = []
    
    for idx, station in stations_opening.iterrows():
        station_name = station['Station Name (English)']
        
        # Get TPUs affected by this station
        affected_tpus = identify_affected_tpus(station_name, opening_year, spatial_join_data)
        
        if len(affected_tpus) > 0:
            # Get before and after data
            before_year = opening_year - 5  # 5 years before
            after_year = opening_year + 5   # 5 years after
            
            before_data = spatial_join_data[
                (spatial_join_data['TPU_ID'].isin(affected_tpus['TPU_ID'])) &
                (spatial_join_data['year'].astype(int) == before_year)
            ]
            
            after_data = spatial_join_data[
                (spatial_join_data['TPU_ID'].isin(affected_tpus['TPU_ID'])) &
                (spatial_join_data['year'].astype(int) == after_year)
            ]
            
            if len(before_data) > 0 and len(after_data) > 0:
                results.append({
                    'station_name': station_name,
                    'opening_year': opening_year,
                    'affected_tpus_count': len(affected_tpus),
                    'before_year': before_year,
                    'after_year': after_year,
                    'before_tpu_count': len(before_data),
                    'after_tpu_count': len(after_data)
                })
    
    if results:
        return pd.DataFrame(results)
    
    return pd.DataFrame()


def temporal_analysis():
    """
    Perform temporal analysis across all years.
    """
    project_root = Path(__file__).parent.parent.parent
    
    # Load spatial join data
    spatial_file = project_root / 'data' / 'analysis' / 'mtr_tpu_spatial_join_all_years.csv'
    
    if not spatial_file.exists():
        print("Error: Spatial join data not found. Run spatial_analysis.py first.")
        return
    
    spatial_data = pd.read_csv(spatial_file)
    
    print("=" * 60)
    print("Temporal Analysis: Before/After MTR Station Openings")
    print("=" * 60)
    
    # Analyze different opening periods
    opening_years = [1979, 1998, 2002, 2003, 2005, 2016]
    
    all_results = []
    
    for year in opening_years:
        results = compare_before_after(year, spatial_data)
        if not results.empty:
            all_results.append(results)
    
    if all_results:
        combined_results = pd.concat(all_results, ignore_index=True)
        
        # Save results
        output_file = project_root / 'data' / 'analysis' / 'temporal_analysis_results.csv'
        combined_results.to_csv(output_file, index=False)
        
        print(f"\nSaved temporal analysis results to {output_file}")
        print(f"Total station openings analyzed: {len(combined_results)}")
    else:
        print("\nNo temporal analysis results generated")
        print("Note: This requires demographic data to show actual changes")
    
    print("\n" + "=" * 60)
    print("Temporal analysis complete!")
    print("=" * 60)
    print("\nNote: Full analysis requires demographic data.")
    print("Once demographic data is available, this script will compare")
    print("demographic changes before and after MTR station openings.")


if __name__ == '__main__':
    temporal_analysis()

