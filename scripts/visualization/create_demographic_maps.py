#!/usr/bin/env python3
"""
Create demographic heatmaps and change maps.
"""

import geopandas as gpd
import pandas as pd
import folium
from pathlib import Path
import os
import json

def create_demographic_heatmap(year: str, demographic_var: str, 
                               output_file: Path = None) -> folium.Map:
    """
    Create a heatmap showing demographic variable by TPU.
    """
    project_root = Path(__file__).parent.parent.parent
    
    # Load TPU data with demographics
    tpu_file = project_root / 'data' / 'processed' / 'demographics' / f'tpu_demographics_{year}.geojson'
    
    if not tpu_file.exists():
        # Fallback to TPU boundaries only
        tpu_file = project_root / 'data' / 'processed' / 'tpu' / f'tpu_boundaries_{year}_processed.geojson'
    
    if not tpu_file.exists():
        print(f"TPU data not found for {year}")
        return None
    
    gdf = gpd.read_file(tpu_file)
    
    # Check if demographic variable exists
    if demographic_var not in gdf.columns:
        print(f"Demographic variable '{demographic_var}' not found")
        print(f"Available columns: {list(gdf.columns)[:10]}")
        return None
    
    # Hong Kong center
    hk_center = [22.3193, 114.1694]
    
    # Create map
    m = folium.Map(location=hk_center, zoom_start=11, tiles='OpenStreetMap')
    
    # Create choropleth
    folium.Choropleth(
        geo_data=json.loads(gdf.to_json()),
        data=gdf,
        columns=['TPU_ID', demographic_var],
        key_on='feature.properties.TPU_ID',
        fill_color='YlOrRd',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=f'{demographic_var} ({year})'
    ).add_to(m)
    
    # Add tooltips
    folium.GeoJson(
        gdf.to_json(),
        style_function=lambda feature: {
            'fillOpacity': 0.1,
            'color': 'black',
            'weight': 1
        },
        tooltip=folium.GeoJsonTooltip(
            fields=['TPU_ID', demographic_var],
            aliases=['TPU ID:', f'{demographic_var}:']
        )
    ).add_to(m)
    
    if output_file:
        os.makedirs(output_file.parent, exist_ok=True)
        m.save(str(output_file))
        print(f"Saved demographic map to {output_file}")
    
    return m


def create_change_map(year1: str, year2: str, demographic_var: str,
                     output_file: Path = None) -> folium.Map:
    """
    Create a map showing demographic changes between two years.
    """
    project_root = Path(__file__).parent.parent.parent
    
    # Load data for both years
    file1 = project_root / 'data' / 'processed' / 'demographics' / f'tpu_demographics_{year1}.geojson'
    file2 = project_root / 'data' / 'processed' / 'demographics' / f'tpu_demographics_{year2}.geojson'
    
    if not file1.exists() or not file2.exists():
        print(f"Data not available for {year1} or {year2}")
        return None
    
    gdf1 = gpd.read_file(file1)
    gdf2 = gpd.read_file(file2)
    
    # Merge and calculate change
    merged = gdf1.merge(
        gdf2[['TPU_ID', demographic_var]],
        on='TPU_ID',
        suffixes=(f'_{year1}', f'_{year2}')
    )
    
    var1 = f'{demographic_var}_{year1}'
    var2 = f'{demographic_var}_{year2}'
    
    # Calculate change
    merged['change'] = merged[var2] - merged[var1]
    merged['change_pct'] = ((merged[var2] - merged[var1]) / merged[var1] * 100).fillna(0)
    
    # Hong Kong center
    hk_center = [22.3193, 114.1694]
    
    # Create map
    m = folium.Map(location=hk_center, zoom_start=11, tiles='OpenStreetMap')
    
    # Create choropleth for change
    folium.Choropleth(
        geo_data=json.loads(merged.to_json()),
        data=merged,
        columns=['TPU_ID', 'change'],
        key_on='feature.properties.TPU_ID',
        fill_color='RdYlGn',
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name=f'Change in {demographic_var} ({year1} to {year2})'
    ).add_to(m)
    
    if output_file:
        os.makedirs(output_file.parent, exist_ok=True)
        m.save(str(output_file))
        print(f"Saved change map to {output_file}")
    
    return m


def create_all_demographic_maps():
    """
    Create demographic maps for all available years and variables.
    """
    project_root = Path(__file__).parent.parent.parent
    output_dir = project_root / 'outputs' / 'maps' / 'demographic_maps'
    os.makedirs(output_dir, exist_ok=True)
    
    print("=" * 60)
    print("Creating Demographic Maps")
    print("=" * 60)
    
    years = ['2001', '2006', '2011', '2016']
    
    # Check what demographic variables are available
    demo_file = project_root / 'data' / 'processed' / 'demographics' / 'tpu_demographics_2011.geojson'
    
    if demo_file.exists():
        gdf = gpd.read_file(demo_file)
        demographic_vars = [col for col in gdf.columns 
                           if col not in ['TPU_ID', 'YEAR', 'geometry']]
        
        print(f"\nFound demographic variables: {demographic_vars}")
        
        # Create maps for each variable and year
        for var in demographic_vars[:5]:  # Limit to first 5 for now
            for year in years:
                output_file = output_dir / f'{var}_{year}_heatmap.html'
                create_demographic_heatmap(year, var, output_file)
        
        # Create change maps
        for var in demographic_vars[:5]:
            for i in range(len(years) - 1):
                year1 = years[i]
                year2 = years[i + 1]
                output_file = output_dir / f'{var}_change_{year1}_to_{year2}.html'
                create_change_map(year1, year2, var, output_file)
    else:
        print("\nNo demographic data available yet.")
        print("Maps will be created once demographic data is processed.")
        print("See: outputs/reports/demographic_download_instructions.md")


if __name__ == '__main__':
    create_all_demographic_maps()

