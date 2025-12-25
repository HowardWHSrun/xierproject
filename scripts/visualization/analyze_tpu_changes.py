#!/usr/bin/env python3
"""
Analyze TPU boundary changes across different census years.
"""

import geopandas as gpd
import pandas as pd
from pathlib import Path
import json
from typing import Dict, List, Tuple
from shapely.geometry import Polygon
from shapely.ops import unary_union

def load_processed_tpu_data(data_dir: str = 'tpu_processed') -> Dict[str, gpd.GeoDataFrame]:
    """
    Load all processed TPU boundary data.
    """
    data_path = Path(data_dir)
    tpu_data = {}
    
    years = ['2001', '2006', '2011', '2016', '2021']
    
    for year in years:
        file_path = data_path / f'tpu_boundaries_{year}_processed.geojson'
        if file_path.exists():
            try:
                gdf = gpd.read_file(file_path)
                tpu_data[year] = gdf
                print(f"Loaded {year}: {len(gdf)} TPUs")
            except Exception as e:
                print(f"Error loading {year}: {e}")
    
    return tpu_data


def compare_boundaries(gdf1: gpd.GeoDataFrame, gdf2: gpd.GeoDataFrame, 
                      year1: str, year2: str) -> Dict:
    """
    Compare TPU boundaries between two years.
    """
    if gdf1 is None or gdf2 is None:
        return None
    
    # Calculate total area for each year
    gdf1_area = gdf1.geometry.area.sum()
    gdf2_area = gdf2.geometry.area.sum()
    
    # Find overlapping TPUs (spatial join)
    gdf1_sindex = gdf1.sindex
    overlaps = []
    
    for idx2, row2 in gdf2.iterrows():
        geom2 = row2.geometry
        possible_matches = list(gdf1_sindex.intersection(geom2.bounds))
        
        for idx1 in possible_matches:
            geom1 = gdf1.iloc[idx1].geometry
            if geom1.intersects(geom2):
                overlap_area = geom1.intersection(geom2).area
                overlap_pct1 = (overlap_area / geom1.area) * 100 if geom1.area > 0 else 0
                overlap_pct2 = (overlap_area / geom2.area) * 100 if geom2.area > 0 else 0
                
                if overlap_pct1 > 50 or overlap_pct2 > 50:  # Significant overlap
                    overlaps.append({
                        'tpu1_id': gdf1.iloc[idx1]['TPU_ID'],
                        'tpu2_id': row2['TPU_ID'],
                        'overlap_pct': max(overlap_pct1, overlap_pct2)
                    })
    
    # Identify new TPUs (in year2 but not significantly overlapping with year1)
    new_tpus = []
    for idx2, row2 in gdf2.iterrows():
        geom2 = row2.geometry
        possible_matches = list(gdf1_sindex.intersection(geom2.bounds))
        
        has_overlap = False
        for idx1 in possible_matches:
            geom1 = gdf1.iloc[idx1].geometry
            if geom1.intersects(geom2):
                overlap_area = geom1.intersection(geom2).area
                overlap_pct = (overlap_area / geom2.area) * 100 if geom2.area > 0 else 0
                if overlap_pct > 50:
                    has_overlap = True
                    break
        
        if not has_overlap:
            new_tpus.append(row2['TPU_ID'])
    
    # Identify removed TPUs (in year1 but not significantly overlapping with year2)
    removed_tpus = []
    gdf2_sindex = gdf2.sindex
    for idx1, row1 in gdf1.iterrows():
        geom1 = row1.geometry
        possible_matches = list(gdf2_sindex.intersection(geom1.bounds))
        
        has_overlap = False
        for idx2 in possible_matches:
            geom2 = gdf2.iloc[idx2].geometry
            if geom1.intersects(geom2):
                overlap_area = geom1.intersection(geom2).area
                overlap_pct = (overlap_area / geom1.area) * 100 if geom1.area > 0 else 0
                if overlap_pct > 50:
                    has_overlap = True
                    break
        
        if not has_overlap:
            removed_tpus.append(row1['TPU_ID'])
    
    return {
        'year1': year1,
        'year2': year2,
        'count1': len(gdf1),
        'count2': len(gdf2),
        'area1': float(gdf1_area),
        'area2': float(gdf2_area),
        'new_tpus': len(new_tpus),
        'removed_tpus': len(removed_tpus),
        'overlaps': len(overlaps),
        'new_tpu_ids': new_tpus[:10],  # Sample
        'removed_tpu_ids': removed_tpus[:10]  # Sample
    }


def analyze_all_changes(tpu_data: Dict[str, gpd.GeoDataFrame]) -> List[Dict]:
    """
    Analyze changes across all available years.
    """
    years = sorted([int(y) for y in tpu_data.keys()])
    changes = []
    
    for i in range(len(years) - 1):
        year1 = str(years[i])
        year2 = str(years[i + 1])
        
        if year1 in tpu_data and year2 in tpu_data:
            print(f"\nComparing {year1} to {year2}...")
            change = compare_boundaries(tpu_data[year1], tpu_data[year2], year1, year2)
            if change:
                changes.append(change)
                print(f"  {year1}: {change['count1']} TPUs")
                print(f"  {year2}: {change['count2']} TPUs")
                print(f"  New TPUs: {change['new_tpus']}")
                print(f"  Removed TPUs: {change['removed_tpus']}")
    
    return changes


def generate_summary_report(changes: List[Dict], output_file: str = 'tpu_analysis_report.md'):
    """
    Generate a markdown report summarizing TPU boundary changes.
    """
    report = []
    report.append("# TPU Boundary Changes Analysis (2001-2021)")
    report.append("")
    report.append("## Overview")
    report.append("")
    report.append("This report analyzes changes in Tertiary Planning Unit (TPU) boundaries across Hong Kong census years.")
    report.append("")
    
    if not changes:
        report.append("**Note:** Limited data available for analysis. Only 2006 TPU boundaries were successfully downloaded.")
        report.append("")
        report.append("## Data Availability")
        report.append("")
        report.append("- ✅ 2006: Available")
        report.append("- ❌ 2001: Not available")
        report.append("- ❌ 2011: Not available")
        report.append("- ❌ 2016: Not available")
        report.append("- ❌ 2021: Not available")
        report.append("")
        report.append("## Recommendations")
        report.append("")
        report.append("To complete the analysis, please:")
        report.append("1. Manually download TPU boundary data from the Esri China Open Data portal")
        report.append("2. Place the GeoJSON files in the `tpu_data/` directory")
        report.append("3. Re-run the analysis script")
        return "\n".join(report)
    
    report.append("## Year-by-Year Changes")
    report.append("")
    
    for change in changes:
        report.append(f"### {change['year1']} → {change['year2']}")
        report.append("")
        report.append(f"- **TPU Count:** {change['count1']} → {change['count2']} ({change['count2'] - change['count1']:+d})")
        report.append(f"- **New TPUs:** {change['new_tpus']}")
        report.append(f"- **Removed TPUs:** {change['removed_tpus']}")
        report.append(f"- **Significant Overlaps:** {change['overlaps']}")
        report.append("")
        
        if change['new_tpus'] > 0:
            report.append(f"**Sample New TPU IDs:** {', '.join(change['new_tpu_ids'][:5])}")
            report.append("")
        
        if change['removed_tpus'] > 0:
            report.append(f"**Sample Removed TPU IDs:** {', '.join(change['removed_tpu_ids'][:5])}")
            report.append("")
    
    report.append("## Major Changes Summary")
    report.append("")
    
    total_new = sum(c['new_tpus'] for c in changes)
    total_removed = sum(c['removed_tpus'] for c in changes)
    
    report.append(f"- **Total New TPUs Created:** {total_new}")
    report.append(f"- **Total TPUs Removed/Merged:** {total_removed}")
    report.append("")
    
    report.append("## Key Observations")
    report.append("")
    report.append("1. TPU boundaries are periodically updated to reflect:")
    report.append("   - Urban development and redevelopment")
    report.append("   - Population changes")
    report.append("   - Administrative adjustments")
    report.append("")
    report.append("2. New TPUs typically indicate:")
    report.append("   - New development areas")
    report.append("   - Subdivision of existing areas")
    report.append("   - New Town developments")
    report.append("")
    report.append("3. Removed TPUs may indicate:")
    report.append("   - Merging of small TPUs")
    report.append("   - Administrative consolidation")
    report.append("   - Boundary realignment")
    report.append("")
    
    return "\n".join(report)


def main():
    """
    Main analysis function.
    """
    print("=" * 60)
    print("TPU Boundary Change Analysis")
    print("=" * 60)
    
    # Load processed data
    tpu_data = load_processed_tpu_data()
    
    if not tpu_data:
        print("No TPU data available for analysis.")
        return
    
    # Analyze changes
    changes = analyze_all_changes(tpu_data)
    
    # Generate report
    report = generate_summary_report(changes)
    
    # Save report
    with open('tpu_analysis_report.md', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n{'='*60}")
    print("Analysis complete!")
    print(f"Report saved to: tpu_analysis_report.md")
    print(f"{'='*60}")
    
    # Save changes data as JSON
    with open('tpu_changes.json', 'w') as f:
        json.dump(changes, f, indent=2, default=str)
    
    print(f"Changes data saved to: tpu_changes.json")


if __name__ == '__main__':
    main()

