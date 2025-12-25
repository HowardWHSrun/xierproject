#!/usr/bin/env python3
"""
Download demographic data from data.gov.hk for Hong Kong TPU-level statistics.
"""

import requests
import pandas as pd
from pathlib import Path
import os
import json
import time

# Data.gov.hk datasets for TPU-level demographics
DATA_GOV_DATASETS = {
    '2021': {
        'name': '2021 Population Census by Large TPU',
        'dataset_id': 'hk-censtatd-census_geo-2021-population-census-by-ltpu',
        'url': 'https://data.gov.hk/en-data/dataset/hk-censtatd-census_geo-2021-population-census-by-ltpu'
    },
    '2016': {
        'name': '2016 Population By-census by Small TPU',
        'dataset_id': 'hk-censtatd-census_geo-2016-population-bycensus-by-stpu',
        'url': 'https://data.gov.hk/en-data/dataset/hk-censtatd-census_geo-2016-population-bycensus-by-stpu'
    }
}

def download_from_data_gov(dataset_id: str, output_dir: Path):
    """
    Attempt to download data from data.gov.hk.
    """
    print(f"Attempting to download from data.gov.hk: {dataset_id}")
    
    # Try API endpoint
    api_url = f"https://api.data.gov.hk/v1/facility-dataset/{dataset_id}"
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    
    try:
        response = requests.get(api_url, headers=headers, timeout=30)
        if response.status_code == 200:
            data = response.json()
            # Save raw data
            output_file = output_dir / f'{dataset_id}_raw.json'
            with open(output_file, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"  Downloaded metadata to {output_file}")
            return True
    except Exception as e:
        print(f"  API download failed: {e}")
    
    # Try direct data URL patterns
    data_urls = [
        f"https://data.gov.hk/d/{dataset_id}.csv",
        f"https://data.gov.hk/d/{dataset_id}.xlsx",
        f"https://www.data.gov.hk/d/{dataset_id}.csv",
    ]
    
    for url in data_urls:
        try:
            response = requests.get(url, headers=headers, timeout=30)
            if response.status_code == 200:
                # Determine file type
                if 'csv' in url:
                    output_file = output_dir / f'{dataset_id}.csv'
                    with open(output_file, 'wb') as f:
                        f.write(response.content)
                    print(f"  Downloaded CSV to {output_file}")
                    return True
                elif 'xlsx' in url:
                    output_file = output_dir / f'{dataset_id}.xlsx'
                    with open(output_file, 'wb') as f:
                        f.write(response.content)
                    print(f"  Downloaded Excel to {output_file}")
                    return True
        except Exception as e:
            continue
    
    return False


def main():
    """
    Main function to download demographic data from data.gov.hk.
    """
    project_root = Path(__file__).parent.parent.parent
    
    print("=" * 60)
    print("Downloading Demographic Data from data.gov.hk")
    print("=" * 60)
    
    for year, info in DATA_GOV_DATASETS.items():
        print(f"\n{year}: {info['name']}")
        
        output_dir = project_root / 'data' / 'raw' / 'demographics' / f'census_{year}'
        os.makedirs(output_dir, exist_ok=True)
        
        success = download_from_data_gov(info['dataset_id'], output_dir)
        
        if not success:
            print(f"  Could not download automatically")
            print(f"  Please visit: {info['url']}")
            print(f"  And download manually to: {output_dir}")
    
    print("\n" + "=" * 60)
    print("Download attempt complete!")
    print("=" * 60)
    print("\nNote: If automatic download failed, please:")
    print("1. Visit the data.gov.hk links above")
    print("2. Download the datasets manually")
    print("3. Place files in data/raw/demographics/census_{YEAR}/")
    print("4. Run: python scripts/data_processing/process_demographics.py")


if __name__ == '__main__':
    main()

