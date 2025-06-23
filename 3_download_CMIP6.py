import os
import time
import pexpect
from multiprocessing import Pool, cpu_count


# working_dir = '/data/reloclim/normal/CMIP6_ars/'  # data
working_dir = '/reloclim/ars/INTERACT/CMIP6/'  # big data

table_ids = ['6hrPlevPt', '6hrLev', '6hrPlev', '3hr']  # all
# table_ids = ['6hrPlev', '3hr']  # precipitation
# table_ids = ['6hrPlevPt']  # pressure level data
# table_ids = ['6hrLev']  # model level data

varss = {
    '6hrPlevPt': ['zg'],
    '6hrLev': ['hus', 'ta', 'va', 'ua'],
    '6hrPlev': ['pr'],
    '3hr': ['pr']
    }
# exps = ['historical', 'ssp585']
# exps = ['ssp585']
exps = ['ssp585']
run = 'r1i1p1f1'

# # hist
# gcms = [
#     # 'GISS-E2-1-G',  # 3h pr, done 
#     # 'NorESM2-LM',  # done
#     # 'IPSL-CM6A-LR-INCA',  # done
#     # 'IPSL-CM6A-LR',  # done
#     # 'MPI-ESM1-2-LR',  # done
#     # 'AWI-ESM-1-1-LR',  # done
#     # 'MPI-ESM-1-2-HAM',  # done
#     # 'MIROC6',  # done
#     # 'MRI-ESM2-0',  # 3h pr, 
#     # 'TaiESM1',  # done
#     # 'NorESM2-MM',  # done
#     # 'MPI-ESM1-2-HR',  # done
#     # 'CMCC-CM2-SR5',  # done
#     # 'CMCC-ESM2',
#     # 'EC-Earth3',
#     ]

# ssp585
gcms = [
    # 'NorESM2-LM',
    # 'IPSL-CM6A-LR',
    # 'MPI-ESM1-2-LR',
    # 'MIROC6',
    # 'MRI-ESM2-0', 
    'TaiESM1',
    # 'NorESM2-MM',
    # 'MPI-ESM1-2-HR',
    # 'CMCC-CM2-SR5', 
    # 'CMCC-ESM2',
    # 'EC-Earth3',
    ]

# Load credentials securely (Set these as environment variables instead of hardcoding)
OPENID = os.getenv('ESGF_OPENID', 'https://esg-dn1.nsc.liu.se/esgf-idp/openid/ArminSchaffer')
PASSWORD = os.getenv('ESGF_PASSWORD')


def download_model(args):
    """Handles downloading data for a specific model in parallel."""
    gcm, exp = args  # Unpack arguments

    for table_id in table_ids:
        for var in varss[table_id]:
            file_dir = os.path.join(working_dir, f'{gcm}.{exp}.{table_id}')
            file = f'wget_{var}.sh'
            script_path = os.path.join(file_dir, file)

            if not os.path.exists(script_path):
                print(f"Script not found: {script_path}, skipping...")
                continue

            print(f"Starting download for {gcm} - {exp} - {table_id} - {var}")

            # Start the Bash script
            child = pexpect.spawn(f'bash {script_path} -s', cwd=file_dir)
            child.logfile = open(os.path.join(file_dir, 'temp_output.txt'), "wb")

            patterns = ['Enter your openid :', 'Enter password :', pexpect.EOF]

            while True:
                index = child.expect(patterns, timeout=None)
                if index == 0:
                    child.sendline(OPENID)
                elif index == 1:
                    if not PASSWORD:
                        print("Error: ESGF password not set. Use environment variable ESGF_PASSWORD.")
                        return
                    child.sendline(PASSWORD)
                elif index == 2:
                    break

            child.logfile.close()

            # Check for download failures
            with open(os.path.join(file_dir, 'temp_output.txt'), 'r') as echo_file:
                echo_output = echo_file.read()

            if 'download failed' in echo_output:
                print(f'ERROR: Download failed for {gcm} - {exp} - {table_id} - {var}! Retrying after 30 minutes...')
                time.sleep(1800)
                download_model((gcm, exp))  # Recursive retry

                    
if __name__ == "__main__":
    num_workers = min(len(gcms), cpu_count())  # Use available CPU cores efficiently
    with Pool(processes=num_workers) as pool:
        pool.map(download_model, [(gcm, exp) for gcm in gcms for exp in exps])

    print("All downloads completed.")
