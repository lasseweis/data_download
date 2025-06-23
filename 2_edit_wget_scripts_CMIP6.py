# 2_edit_wget_scripts_CMIP6.py (Automatisiert für beide Zeiträume)
import os
import numpy as np

# NEUER SPEICHERORT, der das 'wget_scripts' Verzeichnis enthält
working_dir = '/nas/home/vlw/Desktop/STREAM/data-download-files/'
# =================================================================

# Konfiguration für beide Durchläufe
run_configurations = [
    {'name': 'historical', 'years': range(1850, 2015)},
    {'name': 'ssp585', 'years': range(2015, 2101)}
]

# Gewünschte Variablen
variables_to_download = ['pr', 'tas', 'ua']
table_id = 'Amon'

# Ihre Modell-Liste
gcms = [
    'HadGEM3-GC31-MM', 'E3SM-1-0', 'CNRM-ESM2-1', 'CNRM-CM6-1', 'CNRM-CM6-1-HR',
    'BCC-CSM2-MR', 'UKESM1-0-LL', 'NorESM2-MM', 'MRI-ESM2-0', 'MPI-ESM1-2-LR',
    'MPI-ESM1-2-HR', 'MIROC-ES2L', 'KIOST-ESM', 'KACE-1-0-G', 'IPSL-CM6A-LR',
    'INM-CM5-0', 'INM-CM4-8', 'IITM-ESM', 'HadGEM3-GC31-LL', 'GFDL-ESM4',
    'EC-Earth3', 'EC-Earth3-Veg-LR', 'EC-Earth3-CC', 'CMCC-ESM2', 'CMCC-CM2-SR5',
    'CESM2', 'CESM2-WACCM', 'CanESM5', 'ACCESS-ESM1-5', 'ACCESS-CM2'
]

# Schleife über beide Konfigurationen (historical und ssp585)
for config in run_configurations:
    exp = config['name']
    years = config['years']
    print(f"\n{'='*20}\nStarte Verarbeitung für: {exp.upper()}\n{'='*20}")

    for gcm in gcms:
        print(f"Verarbeite: {gcm}, {exp}")
        for var in variables_to_download:
            infile_path = os.path.join(working_dir, 'wget_scripts', f'wget_{gcm}_{exp}_{var}_{table_id}.sh')
            outdir = os.path.join(working_dir, f'{gcm}.{exp}.{table_id}/')
            outfile_path = os.path.join(outdir, f'wget_{var}.sh')

            if not os.path.exists(infile_path):
                continue

            os.makedirs(outdir, exist_ok=True)

            with open(infile_path, 'r') as infile:
                lines = infile.readlines()

            with open(outfile_path, 'w') as outfile:
                for line in lines:
                    try:
                        filename = line.strip().split('/')[-1]
                        date_part = filename.split('_')[-1].replace('.nc', '')
                        year_start = int(date_part.split('-')[0][:4])
                        year_end = int(date_part.split('-')[1][:4])
                        if year_start <= np.max(years) and year_end >= np.min(years):
                            outfile.write(line)
                    except (IndexError, ValueError):
                        outfile.write(line)

print("\nVerarbeitung für alle Zeiträume abgeschlossen.")