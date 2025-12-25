# Instructions for Downloading Hong Kong Demographic Data

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
