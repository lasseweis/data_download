# 3_download_CMIP6.py
import os
import pexpect
from multiprocessing import Pool, cpu_count

# NEUER SPEICHERORT, wo die von Skript 2 aufbereiteten Ordner liegen
script_source_dir = '/nas/home/vlw/Desktop/STREAM/data-download-files/'
# ======================================================================

# Definieren Sie hier Ihre Zielordner für jede Variable
target_dirs = {
    'pr': '/data/users/vlw/paper1-cmip-data/pr',
    'tas': '/data/users/vlw/paper1-cmip-data/tas',
    'ua': '/data/users/vlw/paper1-cmip-data/ua'
}

# Konfiguration der zu ladenden Daten
table_id = 'Amon'
variables_to_download = ['pr', 'tas', 'ua']
exps = ['historical', 'ssp585']

# Ihre Modell-Liste
gcms = [
    'HadGEM3-GC31-MM', 'E3SM-1-0', 'CNRM-ESM2-1', 'CNRM-CM6-1', 'CNRM-CM6-1-HR',
    'BCC-CSM2-MR', 'UKESM1-0-LL', 'NorESM2-MM', 'MRI-ESM2-0', 'MPI-ESM1-2-LR',
    'MPI-ESM1-2-HR', 'MIROC-ES2L', 'KIOST-ESM', 'KACE-1-0-G', 'IPSL-CM6A-LR',
    'INM-CM5-0', 'INM-CM4-8', 'IITM-ESM', 'HadGEM3-GC31-LL', 'GFDL-ESM4',
    'EC-Earth3', 'EC-Earth3-Veg-LR', 'EC-Earth3-CC', 'CMCC-ESM2', 'CMCC-CM2-SR5',
    'CESM2', 'CESM2-WACCM', 'CanESM5', 'ACCESS-ESM1-5', 'ACCESS-CM2'
]

# Anmeldedaten aus Umgebungsvariablen laden
OPENID = 'aaa'
PASSWORD = 'ESGF_PASSWORD'

def download_task(args):
    """Führt den Download für eine spezifische Kombination aus."""
    gcm, exp, var = args

    if not OPENID or not PASSWORD:
        print("FEHLER: ESGF_OPENID oder ESGF_PASSWORD nicht als Umgebungsvariable gesetzt.")
        return

    download_dir = target_dirs.get(var)
    if not download_dir:
        return

    os.makedirs(download_dir, exist_ok=True)

    script_dir = os.path.join(script_source_dir, f'{gcm}.{exp}.{table_id}')
    script_path = os.path.join(script_dir, f'wget_{var}.sh')

    if not os.path.exists(script_path):
        return

    print(f"Starte Download für: {gcm} - {exp} - {var} --> Ziel: {download_dir}")
    log_file_path = os.path.join(download_dir, f'download_log_{gcm}_{exp}_{var}.txt')

    try:
        child = pexpect.spawn(f'bash {script_path} -s', cwd=download_dir, timeout=600)
        child.logfile_read = open(log_file_path, "wb")
        
        patterns = ['Enter your openid :', 'Enter password :', pexpect.EOF, pexpect.TIMEOUT]
        index = child.expect(patterns)
        if index == 0:
            child.sendline(OPENID)
            index = child.expect(patterns)
            if index == 1:
                child.sendline(PASSWORD)

        child.expect(pexpect.EOF)
        child.close()
    except Exception as e:
        print(f"Ein Fehler ist aufgetreten bei {gcm} - {exp} - {var}: {e}")

if __name__ == "__main__":
    tasks = [(gcm, exp, var) for gcm in gcms for exp in exps for var in variables_to_download]
    
    if not tasks:
        print("Keine Aufgaben zum Herunterladen gefunden.")
    else:
        num_workers = min(len(tasks), cpu_count(), 8)
        print(f"Starte {len(tasks)} Download-Aufgaben mit {num_workers} parallelen Prozessen...")
        with Pool(processes=num_workers) as pool:
            pool.map(download_task, tasks)

    print("Alle Download-Aufgaben abgeschlossen.")