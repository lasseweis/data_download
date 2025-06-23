import os
import sys
import re
import numpy as np
import glob


# working_dir = '/data/reloclim/normal/CMIP6_ars/'  # data
working_dir = '/reloclim/ars/INTERACT/CMIP6/'  # big data

# years = range(1970, 2006)
years = range(2065, 2101)

wget_name_struc = "wget_{gcm}_{exp}_{var}_{table_id}.sh"

freqs = ['6hrPt', '6hrPt', '6hr', '3hr']
table_ids = ['6hrPlevPt', '6hrLev', '6hrPlev', '3hr']
varss = [['hus', 'va', 'ta', 'ua', 'zg'],
        ['hus', 'va', 'ta', 'ua', 'zg'],
        ['pr'],
        ['pr']]
# exps = ['historical', 'ssp585']
exps = ['ssp585']
run = 'r1i1p1f1'

# gcms = [
#     'ACCESS-CM2',
#     'ACCESS-ESM1-5',
#     'AWI-ESM-1-1-LR',
#     'BCC-CSM2-MR',
#     'BCC-ESM1',
#     'CAS-ESM2-0',
#     'CESM2',
#     'CESM2-FV2',
#     'CESM2-WACCM',
#     'CESM2-WACCM-FV2',
#     'CIESM',
#     'CMCC-CM2-HR4',
#     'CMCC-CM2-SR5',
#     'CMCC-ESM2',
#     'CanESM5',
#     'CanESM5-1',
#     'E3SM-1-0',
#     'E3SM-1-1',
#     'E3SM-1-1-ECA',
#     'E3SM-2-0',
#     'E3SM-2-0-NARRM',
#     'EC-Earth3',
#     'EC-Earth3-AerChem',
#     'EC-Earth3-CC',
#     'EC-Earth3-Veg',
#     'EC-Earth3-Veg-LR',
#     'FGOALS-f3-L',
#     'FGOALS-g3',
#     'GFDL-CM4',
#     'GFDL-ESM',
#     'GFDL-ESM4',
#     'GISS-E2-1-G',
#     'GISS-E2-1-H',
#     'GISS-E2-2-G',
#     'GISS-E2-2-H',
#     'IPSL-CM5A2-INCA',
#     'IPSL-CM6A-LR',
#     'IPSL-CM6A-LR-INCA',
#     'KACE-1-0-G',
#     'KIOST-ESM',
#     'MCM-UA-1-0',
#     'MIROC6',
#     'MPI-ESM-1-2-HAM',
#     'MPI-ESM1-2-HR',
#     'MPI-ESM1-2-LR',
#     'MRI-ESM2-0',
#     'NESM3',
#     'NorCPM1',
#     'NorESM2-LM',
#     'NorESM2-MM',
#     'SAM0-UNICON',
#     'SAM0-UNICONACCESS-CM2',
#     'TaiESM1'
# ]

gcms = [
#  'MPI-ESM1-2-HR',
#  'MPI-ESM1-2-LR',
#  'MRI-ESM2-0',
 'NorESM2-LM',
#  'NorESM2-MM',
#  'TaiESM1'
 ]

# force differnt data node
old_url = '//esgf.rcec.sinica.edu.tw/thredds/fileServer/my_cmip6_dataroot/ScenarioMIP'
new_url = '//esgf.rcec.sinica.edu.tw/thredds/fileServer/my_cmip6_dataroot/ScenarioMIP'

for gcm in gcms:
    for exp in exps:        
        # check if all variables are available on model levels or all 5 on plev
        files = glob.glob(os.path.join(working_dir, 'wget_scripts/', f'wget_{gcm}_{exp}_*_6hrLev.sh'))
        if len(files) < 4:
            files = glob.glob(os.path.join(working_dir, 'wget_scripts/', f'wget_{gcm}_{exp}_*_6hrPlevPt.sh'))
            if len(files) < 5:
                continue
        
        # check if precipitation is available
        files = glob.glob(os.path.join(working_dir, 'wget_scripts/', f'wget_{gcm}_{exp}_pr_*.sh'))
        if len(files) < 1:
            continue

        # check if zg is available on plev
        files = glob.glob(os.path.join(working_dir, 'wget_scripts/', f'wget_{gcm}_{exp}_zg_*.sh'))
        if len(files) < 1:
            continue
        
        print(gcm, exp)

        for i, table_id in enumerate(table_ids):
            for var in varss[i]:
                infile = f'wget_{gcm}_{exp}_{var}_{table_id}.sh'
                outdir = os.path.join(working_dir, f'{gcm}.{exp}.{table_id}/')
                outfile = f'wget_{var}.sh'

                if not os.path.exists(outdir):
                    os.makedirs(outdir)

                # os.system(f'cp {os.path.join(indir, infile)} {os.path.join(outdir, outfile)}')
                # Read in the file
                try:
                    with open(os.path.join(working_dir, 'wget_scripts/', infile), 'r') as file:
                        lines = file.readlines()

                    # Write the file out again
                    with open(os.path.join(outdir, outfile), 'w') as file:
                        for line in lines:
                            if f'{var}_{table_id}_{gcm}_{exp}' in line:
                                line_seg_year1 = int(line.split(' ')[0].split('_')[-1].split('-')[0][:4])
                                line_seg_year2 = int(line.split(' ')[0].split('_')[-1].split('-')[-1][:4])

                                if (line_seg_year1 > np.max(years)) | (line_seg_year2 < np.min(years)):
                                    continue
                            
                            if old_url in line:
                                line = line.replace(old_url, new_url)

                            file.write(line)
                except:
                    pass

# # special case
# var_list = ['hus', 'va', 'ta', 'ua', 'zg', 'pr']

# for gcm in gcms:
#     for exp in exps:
#         print(gcm, exp)
        
#         files = glob.glob(os.path.join(indir, f'wget_{gcm}_{exp}.sh'))

#         for i, table_id in enumerate(table_ids):
#             for var in varss[i]:
#                 infile = f'wget_{gcm}_{exp}.sh'
#                 outdir = f'/data/reloclim/normal/CMIP6_ars/{gcm}.{exp}.{table_id}/'
#                 outfile = f'wget_{var}.sh'

#                 if not os.path.exists(outdir):
#                     os.makedirs(outdir)

#                 # os.system(f'cp {os.path.join(indir, infile)} {os.path.join(outdir, outfile)}')
#                 # Read in the file
#                 try:
#                     with open(os.path.join(indir, infile), 'r') as file:
#                         lines = file.readlines()

#                     # Write the file out again
#                     with open(os.path.join(outdir, outfile), 'w') as file:
#                         for line in lines:
#                             exclude_line = False

#                             if f'{var}_{table_id}_{gcm}_{exp}' in line:
#                                 line_seg_year1 = int(line.split(' ')[0].split('_')[-1].split('-')[0][:4])
#                                 line_seg_year2 = int(line.split(' ')[0].split('_')[-1].split('-')[-1][:4])

#                                 if (line_seg_year1 > np.max(years)) | (line_seg_year2 < np.min(years)):
#                                     continue

#                             for var_excl in (x for x in var_list if x != var):
#                                 if f"'{var_excl}_" in line:
#                                     exclude_line = True
#                                     break

#                             if exclude_line:
#                                 continue

#                             file.write(line)
#                 except:
#                     pass