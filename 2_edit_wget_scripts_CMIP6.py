import os
import numpy as np
import re # Importieren, um Dateinamen sicher zu parsen

# Der übergeordnete Ordner, der alle Verzeichnisse enthält
working_dir = '/nas/home/vlw/Desktop/STREAM/data-download-files/'
# =================================================================

# Konfiguration der Zeiträume, um die Jahresbereiche für die Filterung zu definieren
run_configurations = {
    'historical': {'years': range(1850, 2015)},
    'ssp585': {'years': range(2015, 2101)}
}

# Variable für die Dateinamen (wird aus Dateiname gelesen, aber als Fallback behalten)
table_id_default = 'Amon'

# =================================================================================
# <<< GEÄNDERT: Vollautomatische Verarbeitung statt manueller Liste >>>
# Das Skript durchsucht jetzt den Ordner mit den heruntergeladenen Skripten.
# =================================================================================

# Pfad zum Verzeichnis mit den neu generierten wget-Skripten
scripts_dir = os.path.join(working_dir, 'wget_scripts_missing')

print(f"\n{'='*20}\nStarte automatische Verarbeitung der Skripte in:\n{scripts_dir}\n{'='*20}")

# Prüfen, ob das Verzeichnis überhaupt existiert
if not os.path.isdir(scripts_dir):
    print("INFO: Verzeichnis mit den zu verarbeitenden Skripten nicht gefunden. Breche ab.")
    exit()

# Alle .sh-Dateien im Verzeichnis finden
script_files = [f for f in os.listdir(scripts_dir) if f.endswith('.sh')]

if not script_files:
    print("INFO: Keine neuen .sh-Skripte zur Verarbeitung gefunden.")
    exit()

for filename in script_files:
    # Informationen direkt aus dem Dateinamen extrahieren
    # Format: wget_{gcm}_{exp}_{var}_{table_id}.sh
    match = re.match(r'wget_(.+)_(historical|ssp585)_(.+)_(.+)\.sh', filename)
    
    if not match:
        print(f"WARNUNG: Dateiname '{filename}' hat kein erwartetes Format. Überspringe.")
        continue
        
    gcm, exp, var, table_id = match.groups()
    
    print(f"Verarbeite: {gcm}, {exp}, {var} (aus Datei: {filename})")

    # Den korrekten Jahresbereich für das aktuelle Experiment holen
    if exp not in run_configurations:
        print(f"WARNUNG: Unbekanntes Experiment '{exp}' für {gcm}. Überspringe.")
        continue
    years = run_configurations[exp]['years']

    # Pfad zur Quelldatei
    infile_path = os.path.join(scripts_dir, filename)
    
    # Zieldatei und -ordner definieren
    outdir = os.path.join(working_dir, f'{gcm}.{exp}.{table_id}/')
    outfile_path = os.path.join(outdir, f'wget_{var}.sh')

    os.makedirs(outdir, exist_ok=True)

    with open(infile_path, 'r') as infile:
        lines = infile.readlines()

    # <<< WICHTIGE ÄNDERUNG: Datei im 'write'-Modus ('w') öffnen >>>
    # Dies überschreibt eine eventuell vorhandene alte Datei und verhindert so
    # die Ansammlung von doppelten Download-Links bei wiederholter Ausführung.
    with open(outfile_path, 'w') as outfile:
        outfile.write(f"# Dieses Skript wurde automatisch generiert oder aktualisiert.\n")
        outfile.write(f"# Quelle: {filename}\n#\n")
        
        for line in lines:
            # Filtere die Zeilen nach dem korrekten Jahresbereich
            # Dies ist nützlich, falls der ESGF-Knoten auch Daten außerhalb des gewünschten Bereichs liefert
            try:
                line_filename = line.strip().split('/')[-1]
                date_part = line_filename.split('_')[-1].replace('.nc', '')
                year_start = int(date_part.split('-')[0][:4])
                year_end = int(date_part.split('-')[1][:4])
                
                # Nur Links behalten, die sich mit dem gewünschten Zeitraum überschneiden
                if year_start <= np.max(years) and year_end >= np.min(years):
                    outfile.write(line)
            except (IndexError, ValueError):
                # Schreibe Zeilen, die nicht geparst werden können (z.B. Kommentare '#!/bin/bash'), trotzdem in die Datei
                if line.strip(): # Nur nicht-leere Zeilen schreiben
                    outfile.write(line)

print("\nVerarbeitung der nachgeladenen Skripte abgeschlossen.")