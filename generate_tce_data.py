"""
This code downloads .xml files for all TESS-SPOC TCEs across sectors 36-80
and parses and stores data from each sector in .csv files
before removing them.

the .xml files are downloaded using DV retrieval scripts available at: 
https://archive.stsci.edu/hlsp/tess-spoc#section-bba40181-db43-4264-bd40-80b1a5a73175
"""
import warnings
import requests
import argparse
import os
import glob
from pathlib import Path

# parser input arguments
try:
    parser = argparse.ArgumentParser(
        description="Inputs for TCE data generation"
    )

    parser.add_argument(
        "--sector_min",
        default=None,
        type=str,
        required=True,
        help="minimum sector to parse (e.g., 's0036')",
    )
    parser.add_argument(
        "--sector_max",
        default=None,
        type=str,
        required=True,
        help="maximum sector to parse (e.g., 's0080')",
    )
    parser.add_argument(
        "--output_dir",
        default=None,
        type=str,
        required=True,
        help="Directory to store .csv file of TCE metrics",
    )
    parser.add_argument(
        "--download_xml",
        default=None,
        type=str,
        required=True,
        help="'True' or 'False'; if 'True',  will download .xml files associated with each sector",
    )
    parser.add_argument(
        "--multi_sector",
        default=False,
        type=str,
        required=False,
        help="'True' or 'False'; if 'True',  will download data for multi-sector run with specified sector min/max."
    )

    args = parser.parse_args()
    SECTOR_MIN = args.sector_min
    SECTOR_MAX = args.sector_max
    OUTPUT_DIR = args.output_dir
    DOWNLOAD_XML = args.download_xml
    MULTI_SECTOR = args.multi_sector

except SystemExit:
    warnings.warn("No arguments were parsed from the command line")

# create directory to store outputs
output_dir = Path(OUTPUT_DIR)
output_dir.mkdir(exist_ok=True)

# paths to save retrieval scripts to
retrieval_script_dir = Path("./dv_retrieval_scripts/")
retrieval_script_dir.mkdir(exist_ok=True)
xml_script_dir = Path("./xml_only_retrieval_scripts/")
xml_script_dir.mkdir(exist_ok=True)

# url location of DV retrieval scripts
base_path = 'https://archive.stsci.edu/hlsps/tess-spoc/download_scripts/'

# convert sectors to numbers for iteration
sector_min_n = int(SECTOR_MIN.replace('s',''))
sector_max_n = int(SECTOR_MAX.replace('s',''))
print(f'storing data for sectors {sector_min_n}-{sector_max_n}')

# determine sectors to iterate over
if MULTI_SECTOR=='True':
    sector_strs = [SECTOR_MIN + '-' + SECTOR_MAX]
else:
    sector_strs = ['s00'+str(i) for i in range(sector_min_n, sector_max_n+1)]
    
# store metrics for each individual sector or multi-sector run
for sector_str in sector_strs:

    # link to MAST portal DV retrieval script
    url = base_path + f"hlsp_tess-spoc_tess_phot_{sector_str}_tess_v1_dl-dv.sh"

    # convert to filename
    filename = url.split('/')[-1]  # Extract filename from URL
    filepath = retrieval_script_dir / filename

    # download file
    print(f"downloading {filename}...")
    response = requests.get(url)

    if response.status_code == 200:
        filepath.write_bytes(response.content)
        print(f"✓ saved {filename}")
    else:
        print(f"✗ failed to download {filename}")

    # write lines that download .xml scripts to separate file
    write_cmd = f"grep '.xml' {filepath} > {xml_script_dir}/{sector_str}.sh"
    os.system(write_cmd)

    # update file permissions so it can run
    chmod_cmd = f"chmod +x {xml_script_dir}/{sector_str}.sh"
    os.system(chmod_cmd)
    print('generated xml-only retreival script')
    print('')

    # run bash script to download data
    print(f"================================================= downloading xml files =================================================")
    download_cmd = f"./{xml_script_dir}/{sector_str}.sh"
    if DOWNLOAD_XML=='True':
        os.system(download_cmd)
    else:
        print('skipping xml download (will only run if data are already downloaded)')
    print('================================================= finished downloading =================================================')
    print('')

    # parse .xml files to generate TCE table
    parse_cmd = f"python parse_dv_reports.py --sector {sector_str} --output_dir ./data/tce_data/"
    os.system(parse_cmd)
    print(f'data stored for sector {sector_str}')
