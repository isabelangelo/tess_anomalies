import pandas as pd
import numpy as np
import glob 
import matplotlib.pyplot as plt
from binary_catalogs import *

# metric thresholds for highest priority batch
odd_even_cutoff=35 # max allowed odd/even depth statistic
snr_cutoff=20 # lowest allowed S/N 
reduced_chisq_cutoff=1.1 # lowest allowed rchisq

# read in dv metrics for all sectors
tce_metrics_filenames = glob.glob('./data/tce_data/tce_dv_metrics_s*.csv')
tce_metrics_filenames.sort()
tces_all = pd.concat((pd.read_csv(i) for i in tce_metrics_filenames))
print('{} TCEs reported across all sectors'.format(len(tces_all)))

def add_quantities(df):
    df_new = df.copy()
    df_new['catalogBinary'] = False
    df_new['matchingPeriodSignals'] = False
    df_new['modelChiSquare_reduced'] = df_new.modelChiSquare/df.modelDegreesOfFreedom
    df_new['oddEvenDepth_sig'] = np.sqrt(df_new.oddEvenTransitDepthComparisonStatistic)
    df_new['GhostDiagnostic_chr'] = df_new.coreApertureCorrelationStatistic/df.haloApertureCorrelationStatistic
    df_new['batch_priority'] = np.nan
    return df_new
tces_all = add_quantities(tces_all)

relevant_columns = ['sector', 'ticId', 'toiId', 'planetNumber', 'suspectedEclipsingBinary',
                    'catalogBinary', 'oddEvenTransitDepthComparisonStatistic_significance',
                    'fullConvergence', 'modelChiSquare_reduced', 'modelFitSnr',
                    'oddEvenDepth_sig', 'GhostDiagnostic_chr','batch_priority']

# flag binaries in external catalogs   
catalog_binary_tic_ids = catalog_binary_tic_ids = np.unique(
    prsa2022_catalog.tess_id.tolist() + kostov2025_tbl3.TIC.tolist() + kostov2025_tbl4.TIC.to_list())
tces_all.loc[tces_all.ticId.isin(catalog_binary_tic_ids), 'catalogBinary'] = True

# flag TIC IDs with matching period signals (these are typically missed binaries)
matching_period_tic_ids = []
for idx, row in tces_all.iterrows():
    tic_df = tces_all[tces_all.ticId==row.ticId]
    matching_periods_df = tic_df.query('abs(orbitalPeriodDays-@row.orbitalPeriodDays)<0.01')
    if len(matching_periods_df)>1:
        matching_period_tic_ids.append(row.ticId)
tces_all.loc[tces_all.ticId.isin(matching_period_tic_ids), 'matchingPeriodSignals'] = True

def n_targets(df):
    return len(np.unique(df.ticId))
    
print('sorting {} TICs into batches (ordered from lowest-highest priority)'.format(n_targets(tces_all)))
# priority 0: binaries flagged by TESS pipeline
batch0_condition = tces_all['suspectedEclipsingBinary']==True
batch0 = tces_all[batch0_condition]
tces_filtered = tces_all[~batch0_condition]
print('batch 0 (TESS-flagged binaries): {} targets'.format(n_targets(batch0)))

# priority 0 (lowest): no model convergence
batch1_condition = tces_filtered['fullConvergence']==False
batch1 = tces_filtered[batch1_condition]
tces_filtered = tces_filtered[~batch1_condition]
print('batch 1 (no model convergence): {} targets'.format(n_targets(batch1)))

# priority 2: invalid odd/even depth statistic
batch2_condition = tces_filtered['oddEvenTransitDepthComparisonStatistic_significance']==-1
batch2 = tces_filtered[batch2_condition]
tces_filtered = tces_filtered[~batch2_condition]
print('batch 2 (no valid odd/even depth stats): {} targets'.format(n_targets(batch2)))

# priority 3: catalog binaries
batch3_condition = tces_filtered['catalogBinary']==True
batch3 = tces_filtered[batch3_condition]
tces_filtered = tces_filtered[~batch3_condition]
print('batch 3 (binaries in external catalogs): {} targets'.format(n_targets(batch3)))

# priority 4: suspected background EBs
batch4_condition = tces_filtered['GhostDiagnostic_chr']<1
batch4 = tces_filtered[batch4_condition]
tces_filtered = tces_filtered[~batch4_condition]
print('batch 4 (suspected background EBs): {} targets'.format(n_targets(batch4)))

# priority 5: matching-period signals (likely binaries)
batch5_condition = tces_filtered['matchingPeriodSignals']==True
batch5 = tces_filtered[batch5_condition]
tces_filtered = tces_filtered[~batch5_condition]
print('batch 5 (matching-period signals; likely EBs): {} targets'.format(n_targets(batch5)))

# priority 6: large odd/even depth comparison (likely binaries)
batch6_condition = tces_filtered['oddEvenDepth_sig']>odd_even_cutoff
batch6 = tces_filtered[batch6_condition]
tces_filtered = tces_filtered[~batch6_condition]
print('batch 6 (large odd/even depth difference; likely EBs): {} targets'.format(n_targets(batch6)))

# priority 7: low S/N signals
batch7_condition = tces_filtered['modelFitSnr']<snr_cutoff
batch7 = tces_filtered[batch7_condition]
tces_filtered = tces_filtered[~batch7_condition]
print('batch 7 (low S/N): {} targets'.format(n_targets(batch7)))

# priority 8: low reduced chi-squared
batch8_condition = tces_filtered['modelChiSquare_reduced']<reduced_chisq_cutoff
batch8 = tces_filtered[batch8_condition]
tces_filtered = tces_filtered[~batch8_condition]
print('batch 8 (low rchisq; well-fit by model): {} targets'.format(n_targets(batch8)))

# priority 9: remaining targets (high S/N, large rchisq)
batch9 = tces_filtered.copy()
print('batch 9 (remaining TCEs): {} targets ({} have known planets)'.format(
    n_targets(batch9), 
    n_targets(batch9.query('toiId.notna()'))))

# priority 10: remaining targets (high S/N, large rchisq)
batch10 = tces_all.query('toiId.notna()')
print('batch 10 (all TOIs from original sample): {} targets'.format(
    n_targets(batch10)))


# save as .csv files
print('saving batches to .csv files...')
keys = [str(i) for i in range(0,11)]
values = [batch0, batch1, batch2, batch3, batch4, batch5, batch6, batch7, batch8, batch9, batch10]
batch_dict = dict(zip(keys, values))
for batch_n in batch_dict:
    batch_dict[batch_n].to_csv(f'./data/batch_data/tce_dv_metrics_batch{batch_n}.csv')
