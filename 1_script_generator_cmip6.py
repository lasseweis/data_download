import os
import subprocess
from urllib.parse import urlparse
import itertools
import re
import shutil

# Liste der vollständigen URL-Vorlagen für die verschiedenen ESGF-Knoten.
url_templates = [
    "https://esgf.ceda.ac.uk/esg-search/wget?distrib=true&latest=true&replica=true&realm=atmos&project=CMIP6&experiment_id={exp}&frequency={freq}&table_id={table_id}&member_id={run}&variable={var}&source_id={gcm}&limit=10000",
    "https://esgf-data.dkrz.de/esg-search/wget?distrib=true&latest=true&realm=atmos&project=CMIP6&experiment_id={exp}&frequency={freq}&table_id={table_id}&member_id={run}&variable={var}&source_id={gcm}&limit=10000",
    "https://esgf-node.ipsl.upmc.fr/esg-search/wget?distrib=true&latest=true&realm=atmos&project=CMIP6&experiment_id={exp}&frequency={freq}&table_id={table_id}&member_id={run}&variable={var}&source_id={gcm}&limit=10000",
    "https://esgf-node.ornl.gov/esg-search/wget?distrib=true&latest=true&realm=atmos&project=CMIP6&experiment_id={exp}&frequency={freq}&table_id={table_id}&member_id={run}&variable={var}&source_id={gcm}&limit=10000",
]

# =================================================================================
# Zentrale Konfiguration der Pfade (MIT AUTOMATISCHER BEREINIGUNG)
# =================================================================================
# HIER WIRD NACH VORHANDENEN .nc DATEIEN GESUCHT
data_search_path = r'/data/reloclim/normal/CMIP6_STREAM/paper1-cmip-data/'

# HIER WERDEN GENERIERTE SKRIPTE GESPEICHERT (Arbeitsverzeichnis)
working_dir = r'/nas/home/vlw/Desktop/STREAM/data-download-files/'

# --- Abgeleitete Pfade (werden automatisch erstellt) ---
path_out = os.path.join(working_dir, 'wget_scripts_missing')

# Automatische Bereinigung des Ausgabe-Ordners
if os.path.exists(path_out):
    print(f"Bereinige alten Skript-Ordner: {path_out}")
    shutil.rmtree(path_out)

# Erstelle den Ordner neu und leer.
os.makedirs(path_out)
print(f"Leeres Verzeichnis für neue Skripte erstellt: {path_out}")


# =================================================================================
# Schritt 1: Definition des SOLL-ZUSTANDS (alle gewünschten Datensätze)
# =================================================================================
gcms = [
    'ACCESS-CM2', 'ACCESS-ESM1-5', 'BCC-CSM2-MR', 'CESM2', 'CESM2-WACCM',
    'CMCC-CM2-SR5', 'CMCC-ESM2', 'CNRM-CM6-1', 'CNRM-CM6-1-HR', 'CNRM-ESM2-1',
    'CanESM5', 'E3SM-1-0', 'EC-Earth3', 'EC-Earth3-CC', 'EC-Earth3-Veg-LR',
    'GFDL-ESM4', 'HadGEM3-GC31-LL', 'HadGEM3-GC31-MM', 'IITM-ESM', 'INM-CM4-8',
    'INM-CM5-0', 'IPSL-CM6A-LR', 'KACE-1-0-G', 'KIOST-ESM', 'MIROC-ES2L',
    'MPI-ESM1-2-HR', 'MPI-ESM1-2-LR', 'MRI-ESM2-0', 'NorESM2-MM', 'UKESM1-0-LL',
]
variables = ['pr', 'tas', 'ua']
experiments = ['historical', 'ssp585']
run = 'r1i1p1f1'
table_id = 'Amon'
freq = 'mon'
TARGET_START_YEAR = 1850
TARGET_END_YEAR = 2099


# =================================================================================
# Schritt 2: Automatische Prüfung mit ROBUSTER Dateinamen-Analyse
# =================================================================================
print("="*80)
print(f"Starte finale Überprüfung im Daten-Pfad: {data_search_path}")
print(f"Ziel-Zeitraum: {TARGET_START_YEAR} - {TARGET_END_YEAR}")
print("="*80)

jobs_to_download = []
for gcm, var in itertools.product(gcms, variables):
    
    time_segments = []
    for root, dirs, files in os.walk(data_search_path):
        for filename in files:
            if not filename.endswith('.nc'): continue
            try:
                parts = os.path.basename(filename).replace('.nc', '').split('_')
                if len(parts) < 7: continue
                file_var, file_model, time_range = parts[0], parts[2], parts[6]
                if file_model == gcm and file_var == var:
                    start_date_str, end_date_str = time_range.split('-')
                    start_year = int(start_date_str[:4])
                    end_year = int(end_date_str[:4])
                    time_segments.append((start_year, end_year))
            except (IndexError, ValueError):
                continue

    if not time_segments:
        print(f"  [✗] FEHLT           : {gcm}, {var} | Keine passenden Dateien gefunden.")
        for exp in experiments:
            jobs_to_download.append({'gcm': gcm, 'exp': exp, 'var': var, 'table_id': table_id, 'run': run})
        continue

    time_segments.sort()
    merged_blocks = []
    current_start, current_end = time_segments[0]
    for next_start, next_end in time_segments[1:]:
        if next_start > current_end + 1:
            merged_blocks.append((current_start, current_end))
            current_start, current_end = next_start, next_end
        else:
            current_end = max(current_end, next_end)
    merged_blocks.append((current_start, current_end))

    is_continuous_and_complete = (len(merged_blocks) == 1 and
                                  merged_blocks[0][0] <= TARGET_START_YEAR and
                                  merged_blocks[0][1] >= TARGET_END_YEAR)

    if is_continuous_and_complete:
        start, end = merged_blocks[0]
        print(f"  [✓] Lückenlos      : {gcm}, {var} | Zeitraum: {start}-{end}")
    else:
        found_ranges_str = ", ".join([f"[{start}-{end}]" for start, end in merged_blocks])
        status = "LÜCKENHAFT" if len(merged_blocks) > 1 else "Unvollständig"
        print(f"  [✗] {status.upper():<15s}: {gcm}, {var} | Gefunden: {found_ranges_str}")
        for exp in experiments:
            job = {'gcm': gcm, 'exp': exp, 'var': var, 'table_id': table_id, 'run': run}
            if job not in jobs_to_download:
                jobs_to_download.append(job)

print("\nPrüfung abgeschlossen.")

# =================================================================================
# Schritt 3: Gezielte Erstellung der wget-Skripte für fehlende Daten
# =================================================================================
failed_scripts = []
if not jobs_to_download:
    print("\nAlle benötigten Datensätze sind vollständig und lückenlos vorhanden. Nichts zu tun.")
else:
    print(f"\nStarte die Erstellung von Skripten für {len(jobs_to_download)} fehlende Datensätze...")
    for job in jobs_to_download:
        gcm, exp, var, table_id, run = job.values()
        script_generated = False
        for url_template in url_templates:
            url = url_template.format(exp=exp, freq=freq, table_id=table_id, run=run, var=var, gcm=gcm)
            output_filename = f"wget_{gcm}_{exp}_{var}_{table_id}.sh"
            output_filepath = os.path.join(path_out, output_filename)
            hostname = urlparse(url_template).hostname
            print(f"\nVersuche, Skript zu generieren für: GCM={gcm}, Exp={exp}, Var={var} bei {hostname}")
            try:
                subprocess.run(['wget', url, '-O', output_filepath], check=True, capture_output=True, text=True, timeout=60)
                if os.path.exists(output_filepath) and os.path.getsize(output_filepath) > 100:
                    with open(output_filepath, 'r') as f:
                        if 'http' in f.read(): 
                            print(f"-> Erfolgreich generiert: {output_filename}")
                            script_generated = True; break
                        else:
                            os.remove(output_filepath); print("-> Generiertes Skript ist leer. Versuche nächsten Knoten.")
                else:
                    if os.path.exists(output_filepath): os.remove(output_filepath)
                    print("-> Generiertes Skript ist leer. Versuche nächsten Knoten.")
            except (subprocess.TimeoutExpired, subprocess.CalledProcessError):
                print(f"-> Fehler oder Timeout bei {hostname}. Versuche nächsten Knoten.")
            except Exception as e:
                print(f"-> Unerwarteter Fehler: {e}. Versuche nächsten Knoten.")
        if not script_generated:
            missing_info = f"GCM: {gcm}, Experiment: {exp}, Variable: {var}"
            failed_scripts.append(missing_info)
            print(f"WARNUNG: Konnte für {missing_info} von keinem Knoten ein Skript generieren.")

print("\n\nProzess zur Skripterstellung abgeschlossen.")

# =================================================================================
# Finale Zusammenfassung
# =================================================================================
print("\n" + "="*50 + "\nFINALE ZUSAMMENFASSUNG\n" + "="*50)
if not jobs_to_download:
    print("\nAlle Datensätze sind vollständig und auf dem neuesten Stand.")
elif not failed_scripts:
    print(f"\nGlückwunsch! Alle Skripte für die fehlenden Datensätze wurden erfolgreich generiert.")
else:
    print(f"\nWarnung: Für {len(failed_scripts)} Kombination(en) konnte kein Skript generiert werden:")
    for missing in failed_scripts: print(f"  - {missing}")
print("="*50)