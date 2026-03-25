import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd
import argparse
import warnings
import time
import glob
from itertools import chain
from tqdm import tqdm

# parser input arguments
try:
    parser = argparse.ArgumentParser(
        description="Inputs for TESS-SPOC DV parser"
    )

    parser.add_argument(
        "--sector",
        default=None,
        type=str,
        required=True,
        help="Sector to store DV metrics for (e.g. 's0055')",
    )
    parser.add_argument(
        "--output_dir",
        default=None,
        type=str,
        required=True,
        help="Directory to store .csv file of TCE metrics",
    )

    args = parser.parse_args()
    SECTOR = args.sector
    OUTPUT_DIR = args.output_dir

except SystemExit:
    warnings.warn("No arguments were parsed from the command line")


print('')
print('reading data validation reports from:{}'.format(SECTOR))
print('storing TCE metrics in:{}'.format(OUTPUT_DIR), end='\n\n')

# filenames of DV files 
dv_filenames = glob.glob(SECTOR + '/target/*/*/*/*/*.xml')
print('found {} TCEs with individual xml files'.format(len(dv_filenames)))

# column names by category
star_property_keys = ['tessMag', 'radius', 'effectiveTemp', 'log10SurfaceGravity', 'log10Metallicity', 'stellarDensity']
target_id_keys = ['ticId', 'toiId', 'planetCandidateCount']
planet_candidate_keys = ['planetNumber','maxSingleEventSigma','maxMultipleEventSigma','robustStatistic','suspectedEclipsingBinary',
                         'modelChiSquare2','modelChiSquareDof2','modelChiSquareGof','modelChiSquareGofDof']
all_transits_fit_keys = ['fullConvergence','modelChiSquare','modelDegreesOfFreedom','modelFitSnr']
model_parameter_keys = ['transitEpochBtjd','minImpactParameter','orbitalPeriodDays','ratioPlanetRadiusToStarRadius',
                        'ratioSemiMajorAxisToStarRadius','transitDurationHours','transitDepthPpm']
weak_secondary_keys = ['mesMad','robustStatistic']
binary_discrimination_keys = ['oddEvenTransitDepthComparisonStatistic']
difference_image_keys = ['sector']
bootstrap_keys = ['significance']
ghost_diagnostic_keys = ['coreApertureCorrelationStatistic', 'haloApertureCorrelationStatistic']


# namespace for stellar property tables
ns = {'dv': 'http://www.nasa.gov/2018/TESS/DV'}

# convert key lists to sets for faster lookup
star_property_keys_set = set(star_property_keys)
model_parameter_keys_set = set(model_parameter_keys)
binary_discrimination_keys_set = set(binary_discrimination_keys)
ghost_diagnostic_keys_set = set(ghost_diagnostic_keys)


def parse_tces(filename):
    """
    Parses contents of TESS-SPOC FFI Data Validation results (.xml file)
    and stores relevant TCE information for the associated TIC in a dictionary.

    Args:
        filename (str): path to .xml file for TIC of interest
    Returns:
        tce_data (dict): dictionary containing data validation metrics for each individual TCE
            recorded in the input TIC DV results.
    
    """
    # load xml file main contents
    tree = ET.parse(filename)
    dvTargetResults = tree.getroot()
    
    # target data: star + limb darkening properties
    target_results_data = {key: dvTargetResults.attrib.get(key, '') for key in target_id_keys}
    for elem in dvTargetResults:
        tag = elem.tag.split('}')[-1]
        if tag in star_property_keys_set:
            target_results_data[tag] = elem.attrib['value']
    dvlimbDarkeningModel = dvTargetResults.find('dv:limbDarkeningModel', ns)
    limb_darkening_data = dvlimbDarkeningModel.attrib
    star_properties = target_results_data | limb_darkening_data
    
    # planet data: fit + candidate metrics, transit properties, binary metrics
    tce_data = []
    for dvplanetResults in dvTargetResults.findall('dv:planetResults', ns):

        # dictionaries to store DV metrics in
        planet_candidate_data = {}
        all_transits_fit_data = {}
        binary_discrimination_data = {}
        bootstrap_data = {}
        model_parameter_data = {}
        difference_image_data = {}
        ghost_diagnostic_data = {}

        # iterate through each recorded TCE
        for elem in dvplanetResults:
            tag = elem.tag.split('}')[-1]
            if tag == 'planetCandidate':
                planet_candidate_data = {key: elem.attrib[key] for key in planet_candidate_keys}
                weak_secondary_data = {key+'_weakSecondary': elem[0].attrib[key] for key in weak_secondary_keys}
            elif tag == 'allTransitsFit':
                all_transits_fit_data = {key: elem.attrib[key] for key in all_transits_fit_keys}
                for param in elem[1]:
                    param_key = param.attrib['name']
                    if param_key in model_parameter_keys_set:
                        model_parameter_data[param_key] = param.attrib['value']
                        model_parameter_data[param_key+'_err'] = param.attrib['uncertainty']
            elif tag == 'differenceImageResults':
                difference_image_data = {key: elem.attrib[key] for key in difference_image_keys}
            elif tag == 'binaryDiscriminationResults':
                for elem_i in elem:
                    tag_i = elem_i.tag.split('}')[-1]
                    if tag_i in binary_discrimination_keys_set:
                        binary_discrimination_data[tag_i] = elem_i.attrib['value']
                        binary_discrimination_data[tag_i+'_significance'] = elem_i.attrib['significance']
            elif tag == 'bootstrapResults':
                bootstrap_data = {'bootstrap_'+key: elem.attrib[key] for key in bootstrap_keys}
            elif tag == 'ghostDiagnosticResults':
                for elem_i in elem:
                    tag_i = elem_i.tag.split('}')[-1]
                    if tag_i in ghost_diagnostic_keys_set:
                        ghost_diagnostic_data[tag_i] = elem_i.attrib['value']
                        ghost_diagnostic_data[tag_i+'_significance'] = elem_i.attrib['significance']
        
        planet_properties =  planet_candidate_data | model_parameter_data | all_transits_fit_data | binary_discrimination_data | bootstrap_data | ghost_diagnostic_data | weak_secondary_data
        tce_data.append(difference_image_data | star_properties | planet_properties)
    return tce_data
    
# create dictionaries for each TCE and store as dataframe
print('loading DV data from files')
# tce_data = list(chain.from_iterable(parse_tces(filename) for filename in dv_filenames))
tce_data = list(chain.from_iterable(
    parse_tces(filename) for filename in tqdm(dv_filenames)
))
print('creating dataframe')
tce_df = pd.DataFrame(tce_data)

# save TCE data to .csv file
tce_data_filename = OUTPUT_DIR + 'tce_dv_metrics_{}.csv'.format(SECTOR)
print('saving dataframe to .csv file')
tce_df.to_csv(tce_data_filename, index=False)
print('TCE data saved to: {}'.format(tce_data_filename), end='\n\n')
