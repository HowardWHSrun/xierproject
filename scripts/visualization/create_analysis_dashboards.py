#!/usr/bin/env python3
"""
Create comprehensive interactive dashboard combining maps, charts, and analysis results.
"""

import pandas as pd
import geopandas as gpd
import folium
from folium import plugins
import json
from pathlib import Path
import os

def create_comprehensive_dashboard(output_file: Path = None):
    """
    Create a comprehensive interactive dashboard.
    """
    project_root = Path(__file__).parent.parent.parent
    
    if output_file is None:
        output_file = project_root / 'outputs' / 'dashboards' / 'interactive_dashboard.html'
    
    os.makedirs(output_file.parent, exist_ok=True)
    
    # Hong Kong center
    hk_center = [22.3193, 114.1694]
    
    # Create base map
    m = folium.Map(location=hk_center, zoom_start=11, tiles='OpenStreetMap')
    
    # Add tile layers
    folium.TileLayer('CartoDB positron', name='CartoDB Positron').add_to(m)
    folium.TileLayer('CartoDB dark_matter', name='CartoDB Dark Matter').add_to(m)
    
    # Load and add TPU boundaries
    years = ['2001', '2006', '2011', '2016']
    year_colors = {
        '2001': '#FF6B6B',
        '2006': '#4ECDC4',
        '2011': '#45B7D1',
        '2016': '#FFA07A'
    }
    
    for year in years:
        tpu_file = project_root / 'data' / 'processed' / 'tpu' / f'tpu_boundaries_{year}_processed.geojson'
        if tpu_file.exists():
            gdf = gpd.read_file(tpu_file)
            color = year_colors.get(year, '#808080')
            
            folium.GeoJson(
                json.loads(gdf.to_json()),
                name=f'TPU Boundaries {year}',
                style_function=lambda feature, color=color: {
                    'fillColor': color,
                    'color': color,
                    'weight': 2,
                    'fillOpacity': 0.2,
                    'opacity': 0.7
                },
                show=False
            ).add_to(m)
    
    # Load and add MTR stations
    mtr_file = project_root / 'data' / 'processed' / 'mtr' / 'mtr_stations_processed.geojson'
    if mtr_file.exists():
        mtr_gdf = gpd.read_file(mtr_file)
        
        mtr_group = folium.FeatureGroup(name='MTR Stations', show=True)
        
        for idx, station in mtr_gdf.iterrows():
            station_name = station.get('Station Name (English)', 'Unknown')
            lat = station.geometry.y
            lon = station.geometry.x
            
            folium.CircleMarker(
                location=[lat, lon],
                radius=8,
                popup=station_name,
                tooltip=station_name,
                color='#FF0000',
                fillColor='#FF0000',
                fillOpacity=0.8,
                weight=2
            ).add_to(mtr_group)
        
        mtr_group.add_to(m)
    
    # Add spatial analysis layer (MTR proximity)
    spatial_file = project_root / 'data' / 'analysis' / 'mtr_tpu_spatial_join_2016.geojson'
    if spatial_file.exists():
        spatial_gdf = gpd.read_file(spatial_file)
        
        # Create proximity visualization
        def style_proximity(feature):
            distance = feature['properties'].get('nearest_mtr_distance', 0)
            if distance < 500:
                return {'fillColor': '#00FF00', 'color': '#00FF00', 'fillOpacity': 0.3}
            elif distance < 1000:
                return {'fillColor': '#FFFF00', 'color': '#FFFF00', 'fillOpacity': 0.3}
            elif distance < 2000:
                return {'fillColor': '#FFA500', 'color': '#FFA500', 'fillOpacity': 0.3}
            else:
                return {'fillColor': '#FF0000', 'color': '#FF0000', 'fillOpacity': 0.3}
        
        folium.GeoJson(
            json.loads(spatial_gdf.to_json()),
            name='MTR Proximity (2016)',
            style_function=style_proximity,
            tooltip=folium.GeoJsonTooltip(
                fields=['TPU_ID', 'nearest_mtr_distance', 'nearest_mtr_station'],
                aliases=['TPU ID:', 'Distance to MTR:', 'Nearest Station:']
            ),
            show=False
        ).add_to(m)
    
    # Add layer control
    folium.LayerControl(collapsed=False).add_to(m)
    
    # Add plugins
    plugins.Fullscreen().add_to(m)
    plugins.MeasureControl().add_to(m)
    
    # Add legend
    legend_html = '''
    <div style="position: fixed; bottom: 50px; right: 50px; width: 250px; height: auto; 
                background-color: white; z-index:9999; font-size:14px;
                border:2px solid grey; border-radius: 5px; padding: 10px">
    <h4 style="margin-top: 0;">Legend</h4>
    <p><strong>TPU Boundaries:</strong></p>
    <p><span style="color: #FF6B6B;">■</span> 2001</p>
    <p><span style="color: #4ECDC4;">■</span> 2006</p>
    <p><span style="color: #45B7D1;">■</span> 2011</p>
    <p><span style="color: #FFA07A;">■</span> 2016</p>
    <hr>
    <p><strong>MTR Proximity:</strong></p>
    <p><span style="color: #00FF00;">■</span> &lt;500m</p>
    <p><span style="color: #FFFF00;">■</span> 500-1000m</p>
    <p><span style="color: #FFA500;">■</span> 1-2km</p>
    <p><span style="color: #FF0000;">■</span> &gt;2km</p>
    <hr>
    <p><span style="color: #FF0000;">●</span> MTR Stations</p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))
    
    # Save dashboard
    m.save(str(output_file))
    print(f"Dashboard saved to {output_file}")
    
    return m


if __name__ == '__main__':
    create_comprehensive_dashboard()

