
*Description*
The following programs identify candidate anomalies in TESS data based on their TESS-SPOC Data Validation reports. 

<ins>step 1</ins>: create the following directories:
`./dv_retrieval_scripts/`
`./xml_only_retrieval_scripts/`

<ins>step 2</ins>: download the DV retrieval scripts for the sectors of interest from:
https://archive.stsci.edu/hlsp/tess-spoc
and store in  `./dv_retrieval_scripts/`.

<ins>step 3</ins>: generate scripts that contain only the `.xml` file retrieval commands:
`grep ".xml" ./dv_retrieval_scripts/hlsp_tess-spoc_tess_phot_s0055_tess_v1_dl-dv.sh > ./xml_only_retrieval_scripts/s0055_xml_only.sh`

<ins>step 4</ins>: run the following programs to create batches of anomaly candidates for follow-up analysis:

generate_tce_data.py: Downloads TCE .xml files and queries files to generate TCE tables with relevant DV metrics.
*xml files are saved to corresponding sector directories (e.g., `./s0036/`, `./s0037/`, etc.). 
*TCE tables are saved to `./data/tce_data/`.

create_tce_batches.py: Sorts TCEs, and generates batches of TCE tables for follow up that are ordered by priority. 
