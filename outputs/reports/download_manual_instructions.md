# Manual Download Instructions for TPU Boundary Data

Since automated downloads from the Esri China Open Data portal require authentication, please follow these steps to manually download the TPU boundary data for other years:

## Steps to Download TPU Boundaries

### For 2011, 2001, 2021, and 2016:

1. Visit the respective dataset pages:
   - **2011**: https://opendata.esrichina.hk/datasets/boundaries-of-tertiary-planning-units-street-blocks-village-clusters-in-hong-kong-for-2011-population-census/explore
   - **2001**: https://opendata.esrichina.hk/datasets/boundaries-of-tertiary-planning-units-street-blocks-village-clusters-in-hong-kong-for-2001-population-census-1/explore
   - **2021**: https://opendata.esrichina.hk/maps/c4c71147985b4be1aade0fb1401530c2/explore
   - **2016**: https://www.arcgis.com/apps/mapviewer/index.html?webmap=9800de8d31f646a9b191a0c8f5cd36c6

2. Click the "Download" button on each page

3. Select "GeoJSON" as the format

4. Save the files to the `tpu_data/` directory with these exact names:
   - `tpu_boundaries_2011.geojson`
   - `tpu_boundaries_2001.geojson`
   - `tpu_boundaries_2021.geojson`
   - `tpu_boundaries_2016.geojson`

5. After downloading, run:
   ```bash
   python process_tpu_data.py
   python create_tpu_mtr_map.py
   ```

The map will automatically include all available years!

