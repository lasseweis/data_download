import os
import subprocess

# List of URLs for the different nodes to try
nodes = [
    "https://esgf-node.ipsl.upmc.fr/esg-search/wget",
    "https://esgf.ceda.ac.uk/esg-search/wget",
    "https://esgf-data.dkrz.de/esg-search/wget",
    "https://esgf-node.ornl.gov/esg-search/wget"
]

# General parameters for the URL
url_params = "?distrib=true&latest=true&replica=true&realm=atmos&project=CMIP6&experiment_id={exp}&frequency={freq}&table_id={table_id}&member_id={run}&variable={var}&source_id={gcm}&limit=10000"

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
# Reading from CMIP6_gcms_list.xlsx is no longer necessary
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
table_ids = ['Amon', 'Amon', 'Amon']  # Corresponding table_id for each variable
runs = ['r1i1p1f1', 'r1i1p1f1', 'r1i1p1f1'] # Corresponding run for each variable
freq = 'mon'
# ---------------------

# Loop through all combinations
for gcm in gcms:
    for exp in experiments:
        for i, var in enumerate(variables):
            table_id = table_ids[i]
            run = runs[i]
            
            script_generated = False
            for node_url in nodes:
                url_struc = node_url + url_params
                url = url_struc.format(exp=exp, freq=freq, table_id=table_id, run=run, var=var, gcm=gcm)
                
                output_filename = f"wget_{gcm}_{exp}_{var}_{table_id}.sh"
                output_filepath = os.path.join(path_out, output_filename)
                
                print(f"\nTrying to generate script for GCM: {gcm}, Exp: {exp}, Var: {var}")
                print(f"Using node: {node_url}")
                
                try:
                    # Execute wget to download the script
                    subprocess.run(['wget', url, '-O', output_filepath], check=True)
                    
                    # Check if the downloaded script is valid (not empty and contains download links)
                    if os.path.exists(output_filepath) and os.path.getsize(output_filepath) > 100:
                        with open(output_filepath, 'r') as f:
                            content = f.read()
                            if 'http' in content: # A simple check for URLs
                                print(f"Successfully generated script: {output_filename}")
                                script_generated = True
                                break  # Exit the node-loop and proceed with the next variable
                            else:
                                print("Generated script is empty or invalid. Trying next node.")
                    else:
                        print("Generated script is empty or was not created. Trying next node.")

                except subprocess.CalledProcessError as e:
                    print(f"Failed to download from {node_url}. Error: {e}. Trying next node.")
                except Exception as e:
                    print(f"An unexpected error occurred: {e}. Trying next node.")

            if not script_generated:
                print(f"----------------------------------------------------------------")
                print(f"WARNING: Could not generate script for {gcm}, {exp}, {var} from any node.")
                print(f"----------------------------------------------------------------")


print("\n\nScript generation process finished.")