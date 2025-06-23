# 1_script_generator_cmip6.py
import urllib.request
import os

# NEUER SPEICHERORT für die generierten .sh Skripte
outdir = '/nas/home/vlw/Desktop/STREAM/data-download-files/wget_scripts/'
# =======================================================================

# Konfiguration der Suchanfrage
url_struc = "https://esgf-node.ipsl.upmc.fr/esg-search/wget?distrib=true&latest=true&project=CMIP6&experiment_id={exp}&frequency=mon&table_id=Amon&member_id={run}&variable={var}&source_id={gcm}&limit=10000"
wget_name_struc = "wget_{gcm}_{exp}_{var}_Amon.sh"

# Gewünschte Variablen in der Monats-Tabelle 'Amon'
variables_to_download = ['pr', 'tas', 'ua']

# Beide Experimente durchsuchen
exps = ['historical', 'ssp585']

# Standard-Ensemble-Mitglied
run = 'r1i1p1f1'

# Ihre Modell-Liste
gcms = [
    'HadGEM3-GC31-MM', 'E3SM-1-0', 'CNRM-ESM2-1', 'CNRM-CM6-1', 'CNRM-CM6-1-HR',
    'BCC-CSM2-MR', 'UKESM1-0-LL', 'NorESM2-MM', 'MRI-ESM2-0', 'MPI-ESM1-2-LR',
    'MPI-ESM1-2-HR', 'MIROC-ES2L', 'KIOST-ESM', 'KACE-1-0-G', 'IPSL-CM6A-LR',
    'INM-CM5-0', 'INM-CM4-8', 'IITM-ESM', 'HadGEM3-GC31-LL', 'GFDL-ESM4',
    'EC-Earth3', 'EC-Earth3-Veg-LR', 'EC-Earth3-CC', 'CMCC-ESM2', 'CMCC-CM2-SR5',
    'CESM2', 'CESM2-WACCM', 'CanESM5', 'ACCESS-ESM1-5', 'ACCESS-CM2'
]

# Erstelle das Ausgabeverzeichnis, falls es nicht existiert
os.makedirs(outdir, exist_ok=True)
print(f"Nutze Ausgabeverzeichnis: {outdir}")

for gcm in gcms:
    for exp in exps:
        for var in variables_to_download:
            print(f"Suche nach: {gcm}, {exp}, {var}, Amon")
            search_url = url_struc.format(gcm=gcm, exp=exp, run=run, var=var)

            try:
                response = urllib.request.urlopen(search_url)
                data = response.read()
                if data == b'No files were found that matched the query':
                    print(f"--> Nicht erfolgreich für: {search_url}")
                else:
                    text = data.decode('utf-8')
                    wget_name = wget_name_struc.format(gcm=gcm, exp=exp, var=var)
                    outpath = os.path.join(outdir, wget_name)
                    with open(outpath, "w") as file:
                        file.write(text)
                    print(f"--> Erfolgreich! Skript gespeichert unter: {outpath}")
            except Exception as e:
                print(f"Fehler bei der Abfrage von {search_url}: {e}")