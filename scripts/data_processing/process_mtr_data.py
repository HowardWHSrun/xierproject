#!/usr/bin/env python3
"""
Process MTR station data and convert to GeoDataFrame for spatial analysis.
"""

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
from pathlib import Path
import os

def load_mtr_stations(excel_file: Path = None) -> gpd.GeoDataFrame:
    """
    Load MTR station data from Excel and convert to GeoDataFrame.
    """
    if excel_file is None:
        project_root = Path(__file__).parent.parent.parent
        excel_file = project_root / 'data' / 'raw' / 'mtr' / 'mtr_stations.xlsx'
    
    print(f"Loading MTR stations from {excel_file}...")
    
    try:
        df = pd.read_excel(excel_file)
        
        # Filter stations with valid coordinates
        df = df[df['Latitude'].notna() & df['Longitude'].notna()]
        df['Latitude'] = pd.to_numeric(df['Latitude'], errors='coerce')
        df['Longitude'] = pd.to_numeric(df['Longitude'], errors='coerce')
        df = df[df['Latitude'].notna() & df['Longitude'].notna()]
        
        # Create geometry from coordinates
        geometry = [Point(lon, lat) for lon, lat in zip(df['Longitude'], df['Latitude'])]
        
        # Create GeoDataFrame
        gdf = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')
        
        print(f"  Loaded {len(gdf)} MTR stations with coordinates")
        return gdf
        
    except Exception as e:
        print(f"Error loading MTR stations: {e}")
        return gpd.GeoDataFrame()


def process_mtr_stations(output_file: Path = None):
    """
    Process MTR station data and save as GeoJSON.
    """
    if output_file is None:
        project_root = Path(__file__).parent.parent.parent
        output_file = project_root / 'data' / 'processed' / 'mtr' / 'mtr_stations_processed.geojson'
    
    os.makedirs(output_file.parent, exist_ok=True)
    
    # Load stations
    gdf = load_mtr_stations()
    
    if len(gdf) > 0:
        # Save as GeoJSON
        gdf.to_file(output_file, driver='GeoJSON')
        print(f"Saved processed MTR stations to {output_file}")
        print(f"Total stations: {len(gdf)}")
    else:
        print("No MTR stations to process")


if __name__ == '__main__':
    process_mtr_stations()

