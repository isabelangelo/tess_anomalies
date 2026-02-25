import pandas as pd
import numpy as np

# ======= Binary catalog from Prsa et al. (2022) ==========================================================
prsa2022_catalog = pd.read_csv('./data/literature_data/prsa2022_binary_catalog.csv')

# Gaia/TESS crossmatch data
doyle2024_tbl2_names = ['TIC','GaiaDR3','GaiaDR2','RAdeg','DEdeg','Nsectors',
         'plx','e_plx','Rplx','Gmag','BP-RP' ,'RV','e_RV','Teff',
         'logg','RUWE','NSS','GMAG','Rad','minNoise','TwoRadius']
doyle2024_tbl2 = pd.read_csv('./data/literature_data/doyle2024_tbl2.dat', sep=r'\s+', names=doyle2024_tbl2_names)
doyle2024_tbl2_singles = doyle2024_tbl2.query('RUWE<1.4')
doyle2024_tbl2_binaries = doyle2024_tbl2.query('RUWE>=1.4')

# ======= new binaries from TESS Ten Thousand catalog (Kostov et al. 2025, Table 3) =========================
# Define column specifications based on the byte positions
colspecs_tbl3 = [
    (0, 10),      # TIC
    (11, 23),     # RAdeg
    (24, 36),     # DEdeg
    (37, 43),     # Tmag
    (44, 53),     # Per
    (54, 63),     # T0-pri
    (64, 67),     # Depth-pri
    (68, 72),     # Dur-pri
    (73, 82),     # T0-sec
    (83, 87),     # Phase
    (88, 94),     # Depth-sec
    (95, 99),     # Dur-sec
    (100, 102),   # Sectors
    (103, 108),   # RUWE
    (109, 117),   # AEN
    (118, 131),   # AENS
    (132, 137),   # Teff
    (138, 250)    # Com
]

names_tbl3 = ['TIC', 'RAdeg', 'DEdeg', 'Tmag', 'Per', 'T0_pri', 'Depth_pri', 
         'Dur_pri', 'T0_sec', 'Phase', 'Depth_sec', 'Dur_sec', 'Sectors', 
         'RUWE', 'AEN', 'AENS', 'Teff', 'Com']

# Read the fixed-width format file
kostov2025_tbl3 = pd.read_fwf('./data/literature_data/kostov2025_tbl3.txt', 
                              colspecs=colspecs_tbl3, 
                              names=names_tbl3, 
                              skiprows=38, 
                              na_values=['', ' '])

# ======= known/recovered binaries from TESS Ten Thousand catalog (Kostov et al. 2025, Table 4) ===========
# Define column specifications based on the byte positions
colspecs_tbl4 = [
    (0, 10),      # TIC
    (11, 23),     # RAdeg
    (24, 36),     # DEdeg
    (37, 46),     # Per-TESS
    (47, 58),     # T0-TESS
    (59, 69),     # Per-Gaia
    (70, 74),     # Ratio1
    (75, 84),     # Per-ASAS
    (85, 89),     # Ratio2
    (90, 100),    # Per-ATLAS
    (101, 105),   # Ratio3
    (106, 115),   # Per-VSX
    (116, 120),   # Ratio4
    (121, 129),   # Per-WISE
    (130, 133),   # Ratio5
    (134, 142),   # Per-ZTF
    (143, 147)    # Ratio6
]

names_tbl4 = ['TIC', 'RAdeg', 'DEdeg', 'Per_TESS', 'T0_TESS', 'Per_Gaia', 
         'Ratio1', 'Per_ASAS', 'Ratio2', 'Per_ATLAS', 'Ratio3', 'Per_VSX', 
         'Ratio4', 'Per_WISE', 'Ratio5', 'Per_ZTF', 'Ratio6']

# Read the fixed-width format file
kostov2025_tbl4 = pd.read_fwf('./data/literature_data/kostov2025_tbl4.txt', 
                              colspecs=colspecs_tbl4,
                              names=names_tbl4,
                              skiprows=36, 
                              na_values=['', ' '])