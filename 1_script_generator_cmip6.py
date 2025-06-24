import os
import subprocess
from urllib.parse import urlparse # NEU: Importiert, um den Hostnamen für die Ausgabe zu extrahieren

# NEU: Liste der vollständigen URL-Vorlagen, wie von Ihnen spezifiziert.
# Jeder String ist eine komplette Vorlage für eine Anfrage.
url_templates = [
    # Ihre bisherigen Knoten
    "https://esgf.ceda.ac.uk/esg-search/wget?distrib=true&latest=true&replica=true&realm=atmos&project=CMIP6&experiment_id={exp}&frequency={freq}&table_id={table_id}&member_id={run}&variable={var}&source_id={gcm}&limit=10000",
    "https://esgf-data.dkrz.de/esg-search/wget?distrib=true&latest=true&realm=atmos&project=CMIP6&experiment_id={exp}&frequency={freq}&table_id={table_id}&member_id={run}&variable={var}&source_id={gcm}&limit=10000",
    "https://esgf-node.ipsl.upmc.fr/esg-search/wget?distrib=true&latest=true&realm=atmos&project=CMIP6&experiment_id={exp}&frequency={freq}&table_id={table_id}&member_id={run}&variable={var}&source_id={gcm}&limit=10000",
    "https://esgf-node.ornl.gov/esg-search/wget?distrib=true&latest=true&realm=atmos&project=CMIP6&experiment_id={exp}&frequency={freq}&table_id={table_id}&member_id={run}&variable={var}&source_id={gcm}&limit=10000",
]


# --- Main path (please adjust if necessary) ---
main_path = r'/nas/home/vlw/Desktop/STREAM/data-download-files'  # <-- PLEASE SET YOUR MAIN PATH HERE
# -----------------------------------------------

# Constructing paths based on the main path
path_out = os.path.join(main_path, 'wget_scripts')

# Create output directory if it doesn't exist
if not os.path.exists(path_out):
    os.makedirs(path_out)
    print(f"Directory created: {path_out}")

# Hardcoded list of GCMs based on the folder structure
gcms = [
    'HadGEM3-GC31-MM', 'E3SM-1-0', 'CNRM-ESM2-1', 'CNRM-CM6-1', 'CNRM-CM6-1-HR',
    'BCC-CSM2-MR', 'UKESM1-0-LL', 'NorESM2-MM', 'MRI-ESM2-0', 'MPI-ESM1-2-LR',
    'MPI-ESM1-2-HR', 'MIROC-ES2L', 'KIOST-ESM', 'KACE-1-0-G', 'IPSL-CM6A-LR',
    'INM-CM5-0', 'INM-CM4-8', 'IITM-ESM', 'HadGEM3-GC31-LL', 'GFDL-ESM4',
    'EC-Earth3', 'EC-Earth3-Veg-LR', 'EC-Earth3-CC', 'CMCC-ESM2', 'CMCC-CM2-SR5',
    'CESM2', 'CESM2-WACCM', 'CanESM5', 'ACCESS-ESM1-5', 'ACCESS-CM2'
]

# --- Configuration ---
experiments = ['historical', 'ssp585']
variables = ['pr', 'tas', 'ua']
table_ids = ['Amon', 'Amon', 'Amon']
runs = ['r1i1p1f1', 'r1i1p1f1', 'r1i1p1f1']
freq = 'mon'
# ---------------------

# Liste zur Verfolgung fehlender Skripte
missing_scripts = []

# Loop through all combinations
for gcm in gcms:
    for exp in experiments:
        for i, var in enumerate(variables):
            table_id = table_ids[i]
            run = runs[i]
            
            script_generated = False
            # GEÄNDERT: Schleife über die neuen, vollständigen URL-Vorlagen
            for url_template in url_templates:
                # GEÄNDERT: Die URL wird jetzt direkt aus der Vorlage formatiert
                url = url_template.format(exp=exp, freq=freq, table_id=table_id, run=run, var=var, gcm=gcm)
                
                output_filename = f"wget_{gcm}_{exp}_{var}_{table_id}.sh"
                output_filepath = os.path.join(path_out, output_filename)
                
                # GEÄNDERT: Die Ausgabe zeigt jetzt den Hostnamen der versuchten URL
                hostname = urlparse(url_template).hostname
                print(f"\nTrying to generate script for GCM: {gcm}, Exp: {exp}, Var: {var}")
                print(f"Using node: {hostname}")
                
                try:
                    subprocess.run(['wget', url, '-O', output_filepath], check=True, capture_output=True, text=True)
                    
                    if os.path.exists(output_filepath) and os.path.getsize(output_filepath) > 100:
                        with open(output_filepath, 'r') as f:
                            content = f.read()
                            if 'http' in content: 
                                print(f"Successfully generated script: {output_filename}")
                                script_generated = True
                                break 
                            else:
                                print("Generated script is empty or invalid. Trying next node.")
                    else:
                        print("Generated script is empty or was not created. Trying next node.")

                except subprocess.CalledProcessError as e:
                    print(f"Failed to download from {hostname}. Error: {e}. Trying next node.")
                except Exception as e:
                    print(f"An unexpected error occurred: {e}. Trying next node.")

            if not script_generated:
                missing_info = f"GCM: {gcm}, Experiment: {exp}, Variable: {var}"
                missing_scripts.append(missing_info)
                print(f"----------------------------------------------------------------")
                print(f"WARNING: Could not generate script for {gcm}, {exp}, {var} from any node.")
                print(f"----------------------------------------------------------------")


print("\n\nScript generation process finished.")

# Finale Zusammenfassung am Ende des Skripts
print("\n" + "="*50)
print("ZUSAMMENFASSUNG DER VERFÜGBARKEIT")
print("="*50)

if not missing_scripts:
    print("\nGlückwunsch! Alle Skripte für alle Modelle und Variablen wurden erfolgreich generiert.")
else:
    print(f"\nWarnung: Für {len(missing_scripts)} Kombination(en) konnte kein Skript generiert werden:")
    for missing in missing_scripts:
        print(f"  - {missing}")
print("="*50)