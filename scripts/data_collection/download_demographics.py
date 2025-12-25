#!/usr/bin/env python3
"""
Download Hong Kong TPU-level demographic data from Census and Statistics Department.
"""

import requests
import pandas as pd
from pathlib import Path
import os
import json

# Hong Kong Census and Statistics Department data sources
CENSUS_SOURCES = {
    '2001': {
        'name': '2001 Population Census',
        'base_url': 'https://www.censtatd.gov.hk',
        'notes': 'Data available from Census and Statistics Department website'
    },
    '2006': {
        'name': '2006 Population By-census',
        'base_url': 'https://www.censtatd.gov.hk',
        'notes': 'Data available from Census and Statistics Department website'
    },
    '2011': {
        'name': '2011 Population Census',
        'base_url': 'https://www.censtatd.gov.hk',
        'notes': 'Data available from Census and Statistics Department website'
    },
    '2016': {
        'name': '2016 Population By-census',
        'base_url': 'https://www.censtatd.gov.hk',
        'notes': 'Data available from Census and Statistics Department website'
    }
}

# Alternative data sources (Planning Department, open data portals)
ALTERNATIVE_SOURCES = {
    'planning_dept': {
        'name': 'Planning Department Statistics',
        'url': 'https://www.pland.gov.hk',
        'notes': 'May have TPU-level statistics'
    },
    'data_gov_hk': {
        'name': 'Data.gov.hk',
        'url': 'https://data.gov.hk',
        'notes': 'Hong Kong open data portal'
    }
}


def research_data_sources():
    """
    Research and document available demographic data sources.
    """
    print("=" * 60)
    print("Researching Hong Kong Demographic Data Sources")
    print("=" * 60)
    
    sources_info = {
        'primary': {
            'name': 'Census and Statistics Department',
            'website': 'https://www.censtatd.gov.hk',
            'description': 'Official source for census and demographic data',
            'data_available': [
                'Population by TPU',
                'Age distribution',
                'Household income',
                'Education attainment',
                'Housing characteristics',
                'Employment statistics'
            ],
            'access_method': 'Website download or API (if available)',
            'years': ['2001', '2006', '2011', '2016']
        },
        'alternative': {
            'planning_dept': {
                'name': 'Planning Department',
                'website': 'https://www.pland.gov.hk',
                'description': 'May have TPU-level planning statistics'
            },
            'data_gov_hk': {
                'name': 'Data.gov.hk',
                'website': 'https://data.gov.hk',
                'description': 'Hong Kong open data portal'
            }
        }
    }
    
    # Save research results
    project_root = Path(__file__).parent.parent.parent
    research_file = project_root / 'outputs' / 'reports' / 'demographic_data_sources.md'
    os.makedirs(research_file.parent, exist_ok=True)
    
    with open(research_file, 'w') as f:
        f.write("# Hong Kong Demographic Data Sources Research\n\n")
        f.write("## Primary Source: Census and Statistics Department\n\n")
        f.write(f"- **Website**: {sources_info['primary']['website']}\n")
        f.write(f"- **Description**: {sources_info['primary']['description']}\n")
        f.write(f"- **Access Method**: {sources_info['primary']['access_method']}\n")
        f.write(f"- **Available Years**: {', '.join(sources_info['primary']['years'])}\n\n")
        f.write("### Available Data:\n")
        for item in sources_info['primary']['data_available']:
            f.write(f"- {item}\n")
        f.write("\n## Alternative Sources\n\n")
        for key, source in sources_info['alternative'].items():
            f.write(f"### {source['name']}\n")
            f.write(f"- **Website**: {source['website']}\n")
            f.write(f"- **Description**: {source['description']}\n\n")
        f.write("## Next Steps\n\n")
        f.write("1. Visit Census and Statistics Department website\n")
        f.write("2. Look for TPU-level statistics in census reports\n")
        f.write("3. Check for downloadable datasets or APIs\n")
        f.write("4. Consider contacting department for data access\n")
        f.write("5. Explore alternative sources if primary source unavailable\n")
    
    print(f"\nResearch results saved to: {research_file}")
    print("\nKey Sources Identified:")
    print(f"1. Census and Statistics Department: {sources_info['primary']['website']}")
    print("2. Planning Department: https://www.pland.gov.hk")
    print("3. Data.gov.hk: https://data.gov.hk")
    
    return sources_info


def download_demographic_data(year: str, output_dir: Path):
    """
    Attempt to download demographic data for a specific year.
    Note: This is a placeholder - actual implementation depends on data source availability.
    """
    print(f"\nAttempting to download {year} demographic data...")
    print("Note: Actual download depends on data source availability and access methods.")
    
    # This would need to be implemented based on actual data source
    # Options include:
    # 1. Direct file download from website
    # 2. API access
    # 3. Web scraping (if data is in HTML tables)
    # 4. Manual download instructions
    
    output_file = output_dir / f'demographics_{year}.csv'
    
    # Placeholder - would need actual implementation
    print(f"  Data would be saved to: {output_file}")
    print("  Implementation needed based on data source format")
    
    return False


def create_download_instructions():
    """
    Create instructions for manually downloading demographic data.
    """
    project_root = Path(__file__).parent.parent.parent
    instructions_file = project_root / 'outputs' / 'reports' / 'demographic_download_instructions.md'
    os.makedirs(instructions_file.parent, exist_ok=True)
    
    instructions = """# Instructions for Downloading Hong Kong Demographic Data

## Primary Source: Census and Statistics Department

### Website
https://www.censtatd.gov.hk

### Steps to Download TPU-Level Data

1. **Navigate to Census Website**
   - Go to https://www.censtatd.gov.hk
   - Look for "Census" or "Population Census" section

2. **Find TPU-Level Statistics**
   - Search for "Tertiary Planning Unit" or "TPU" statistics
   - Look for census reports or statistical tables
   - Check for downloadable datasets (CSV, Excel, or database formats)

3. **Available Census Years**
   - 2001 Population Census
   - 2006 Population By-census
   - 2011 Population Census
   - 2016 Population By-census

4. **Data to Look For**
   - Population by TPU
   - Age distribution by TPU
   - Household income by TPU
   - Education attainment by TPU
   - Housing characteristics by TPU
   - Employment statistics by TPU

5. **Save Files**
   - Download files to: `data/raw/demographics/census_{YEAR}/`
   - Keep original file names or use descriptive names
   - Note the data format (CSV, Excel, etc.)

## Alternative Sources

### Planning Department
- Website: https://www.pland.gov.hk
- May have TPU-level planning and demographic statistics

### Data.gov.hk
- Website: https://data.gov.hk
- Hong Kong open data portal
- Search for "census", "demographics", or "TPU"

## Data Format Requirements

For the analysis to work, demographic data should:
- Include TPU identifiers that match TPU boundary data
- Be in CSV or Excel format (preferred)
- Include multiple demographic variables
- Cover years: 2001, 2006, 2011, 2016

## After Downloading

Once data is downloaded:
1. Place files in appropriate `data/raw/demographics/census_{YEAR}/` directories
2. Run the processing script: `python scripts/data_processing/process_demographics.py`
3. The script will link demographic data to TPU boundaries

## Contact Information

If data is not publicly available:
- Contact Census and Statistics Department for data access
- Email: genenq@censtatd.gov.hk
- Phone: +852 2582 4737
"""
    
    with open(instructions_file, 'w') as f:
        f.write(instructions)
    
    print(f"\nDownload instructions saved to: {instructions_file}")


def main():
    """
    Main function to research and prepare for demographic data download.
    """
    project_root = Path(__file__).parent.parent.parent
    output_dir = project_root / 'data' / 'raw' / 'demographics'
    os.makedirs(output_dir, exist_ok=True)
    
    # Create subdirectories for each census year
    for year in ['2001', '2006', '2011', '2016']:
        os.makedirs(output_dir / f'census_{year}', exist_ok=True)
    
    # Research data sources
    sources = research_data_sources()
    
    # Create download instructions
    create_download_instructions()
    
    print("\n" + "=" * 60)
    print("Demographic Data Research Complete")
    print("=" * 60)
    print("\nNext Steps:")
    print("1. Review the research document: outputs/reports/demographic_data_sources.md")
    print("2. Follow download instructions: outputs/reports/demographic_download_instructions.md")
    print("3. Download demographic data files to data/raw/demographics/")
    print("4. Run process_demographics.py to integrate data")


if __name__ == '__main__':
    main()

