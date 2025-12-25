#!/usr/bin/env python3
"""
Generate comprehensive analysis report with findings, methodology, and recommendations.
"""

import pandas as pd
from pathlib import Path
import os
from datetime import datetime

def generate_final_report():
    """
    Generate comprehensive analysis report.
    """
    project_root = Path(__file__).parent.parent.parent
    output_file = project_root / 'outputs' / 'reports' / 'mtr_impact_report.md'
    os.makedirs(output_file.parent, exist_ok=True)
    
    # Load analysis results
    spatial_file = project_root / 'data' / 'analysis' / 'mtr_tpu_spatial_join_all_years.csv'
    
    report = []
    report.append("# MTR Impact on Hong Kong Demographics: Analysis Report")
    report.append("")
    report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    report.append("## Executive Summary")
    report.append("")
    report.append("This report analyzes the relationship between Mass Transit Railway (MTR) stations")
    report.append("and demographic changes in Hong Kong's Tertiary Planning Units (TPUs) from 2001 to 2016.")
    report.append("")
    
    if spatial_file.exists():
        spatial_data = pd.read_csv(spatial_file)
        
        report.append("## Data Overview")
        report.append("")
        report.append(f"- **TPU Boundaries Analyzed:** 2001, 2006, 2011, 2016")
        report.append(f"- **Total TPU Observations:** {len(spatial_data)}")
        report.append(f"- **MTR Stations:** 99 stations with coordinates")
        report.append("")
        
        # Spatial analysis summary
        report.append("## Spatial Analysis Results")
        report.append("")
        
        for year in ['2001', '2006', '2011', '2016']:
            year_data = spatial_data[spatial_data['year'] == year]
            if len(year_data) > 0:
                report.append(f"### {year}")
                report.append("")
                report.append(f"- **Total TPUs:** {len(year_data)}")
                report.append(f"- **TPUs with MTR stations:** {year_data['has_mtr_station'].sum()}")
                report.append(f"- **TPUs within 500m of MTR:** {year_data['within_500m_buffer'].sum()}")
                report.append(f"- **TPUs within 1000m of MTR:** {year_data['within_1000m_buffer'].sum()}")
                report.append(f"- **Average distance to nearest MTR:** {year_data['nearest_mtr_distance'].mean():.0f}m")
                report.append("")
        
        # Proximity distribution
        report.append("### Proximity Distribution")
        report.append("")
        if 'mtr_proximity_category' in spatial_data.columns:
            proximity_dist = spatial_data['mtr_proximity_category'].value_counts()
            for category, count in proximity_dist.items():
                report.append(f"- **{category}:** {count} TPUs")
            report.append("")
    
    report.append("## Methodology")
    report.append("")
    report.append("### Data Sources")
    report.append("")
    report.append("1. **TPU Boundaries**: Esri China Open Data Portal")
    report.append("   - Years: 2001, 2006, 2011, 2016")
    report.append("   - Source: Planning Department / Census and Statistics Department")
    report.append("")
    report.append("2. **MTR Stations**: Scraped from Wikipedia")
    report.append("   - 99 stations with geographic coordinates")
    report.append("   - Enhanced with geocoding where needed")
    report.append("")
    report.append("3. **Demographic Data**: To be integrated")
    report.append("   - Source: Census and Statistics Department")
    report.append("   - Status: Research completed, download in progress")
    report.append("")
    
    report.append("### Analysis Methods")
    report.append("")
    report.append("1. **Spatial Analysis**:")
    report.append("   - Calculated distance from each TPU centroid to nearest MTR station")
    report.append("   - Created buffer zones (500m, 1000m, 2000m) around MTR stations")
    report.append("   - Identified TPUs containing MTR stations")
    report.append("")
    report.append("2. **Temporal Analysis**:")
    report.append("   - Compare demographics before vs. after MTR station openings")
    report.append("   - Track changes across census years (2001-2016)")
    report.append("")
    report.append("3. **Statistical Analysis**:")
    report.append("   - Correlation analysis between MTR proximity and demographics")
    report.append("   - Group comparisons (MTR-adjacent vs. non-adjacent)")
    report.append("   - Regression analysis to control for other factors")
    report.append("")
    
    report.append("## Key Findings")
    report.append("")
    report.append("### Spatial Patterns")
    report.append("")
    if spatial_file.exists():
        spatial_data = pd.read_csv(spatial_file)
        latest_year = spatial_data[spatial_data['year'] == '2016']
        if len(latest_year) > 0:
            report.append(f"- **{latest_year['has_mtr_station'].sum()} TPUs** contain MTR stations")
            report.append(f"- **{latest_year['within_1000m_buffer'].sum()} TPUs** are within 1km walking distance of MTR stations")
            report.append(f"- **Average distance** to nearest MTR: {latest_year['nearest_mtr_distance'].mean():.0f}m")
            report.append("")
    
    report.append("### Demographic Impact (Pending Data)")
    report.append("")
    report.append("Once demographic data is integrated, this section will include:")
    report.append("- Population changes in MTR-adjacent vs. non-adjacent TPUs")
    report.append("- Income and education level differences")
    report.append("- Housing characteristic changes")
    report.append("- Statistical significance of observed differences")
    report.append("")
    
    report.append("## Limitations")
    report.append("")
    report.append("1. **Demographic Data**: Currently awaiting demographic data integration")
    report.append("2. **MTR Opening Dates**: Using approximate dates; actual dates should be verified")
    report.append("3. **Causality**: Correlation does not imply causation; other factors may influence demographics")
    report.append("4. **TPU Boundary Changes**: Boundary changes across years may affect comparability")
    report.append("")
    
    report.append("## Recommendations")
    report.append("")
    report.append("### For Urban Planning")
    report.append("")
    report.append("1. Consider MTR proximity when planning new developments")
    report.append("2. Monitor demographic changes in areas with new MTR stations")
    report.append("3. Plan for infrastructure needs in MTR-adjacent areas")
    report.append("")
    report.append("### For Future Research")
    report.append("")
    report.append("1. Integrate complete demographic dataset")
    report.append("2. Verify MTR station opening dates from official sources")
    report.append("3. Conduct control group analysis to isolate MTR effects")
    report.append("4. Extend analysis to 2021 census data when available")
    report.append("")
    
    report.append("## Next Steps")
    report.append("")
    report.append("1. Download and integrate demographic data from Census and Statistics Department")
    report.append("2. Verify MTR station opening dates")
    report.append("3. Complete statistical analysis with demographic variables")
    report.append("4. Create detailed visualizations")
    report.append("5. Generate final findings and recommendations")
    report.append("")
    
    report.append("## Files and Outputs")
    report.append("")
    report.append("- **Interactive Map**: `outputs/maps/tpu_mtr_map.html`")
    report.append("- **Dashboard**: `outputs/dashboards/interactive_dashboard.html`")
    report.append("- **Spatial Analysis**: `data/analysis/mtr_tpu_spatial_join_all_years.csv`")
    report.append("- **Analysis Scripts**: `scripts/analysis/`")
    report.append("")
    
    # Write report
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))
    
    print(f"Report saved to {output_file}")
    print("\nReport generated successfully!")
    print("\nNote: Full analysis requires demographic data.")
    print("Once demographic data is integrated, re-run analysis scripts")
    print("and regenerate this report for complete findings.")


if __name__ == '__main__':
    generate_final_report()

