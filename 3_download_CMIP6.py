import os
import pexpect
import re
from multiprocessing import Pool, cpu_count

# Der übergeordnete Ordner, wo die von Skript 2/3 aufbereiteten Ordner liegen
script_source_dir = '/nas/home/vlw/Desktop/STREAM/data-download-files/'
# ======================================================================

# Definieren der Zielordner für jede Variable (unverändert)
target_dirs = {
    'pr': '/data/reloclim/normal/CMIP6_STREAM/paper1-cmip-data/pr',
    'tas': '/data/reloclim/normal/CMIP6_STREAM/paper1-cmip-data/tas',
    'ua': '/data/reloclim/normal/CMIP6_STREAM/paper1-cmip-data/ua'
}

# WICHTIG: Anmeldedaten sicher verwalten (unverändert)
OPENID = '1'
PASSWORD = '2'

# ======================================================================
# Die `download_task` Funktion ist gut konzipiert und bleibt unverändert.
# Sie wird jetzt mit dynamisch gefundenen Jobs aufgerufen.
# ======================================================================
def download_task(job):
    """Führt den Download für einen spezifischen Job aus."""
    gcm = job['gcm']
    exp = job['exp']
    var = job['var']
    table_id = job['table_id']

    if not OPENID or OPENID == 'aaa' or not PASSWORD:
        print("FEHLER: ESGF_OPENID oder ESGF_PASSWORD nicht als Umgebungsvariable gesetzt.")
        return

    download_dir = target_dirs.get(var)
    if not download_dir:
        print(f"WARNUNG: Kein Zielverzeichnis für Variable '{var}' definiert. Überspringe.")
        return

    os.makedirs(download_dir, exist_ok=True)

    script_dir = os.path.join(script_source_dir, f'{gcm}.{exp}.{table_id}')
    script_path = os.path.join(script_dir, f'wget_{var}.sh')

    if not os.path.exists(script_path):
        print(f"INFO: Skriptpfad nicht gefunden, überspringe: {script_path}")
        return

    print(f"Starte Download für: {gcm} - {exp} - {var} --> Ziel: {download_dir}")
    log_file_path = os.path.join(download_dir, f'download_log_AUTO_{gcm}_{exp}_{var}.txt')

    try:
        child = pexpect.spawn(f'bash {script_path}', cwd=download_dir, timeout=3600) # Timeout auf 1h erhöht
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
        if child.exitstatus == 0:
            print(f"-> ERFOLGREICH abgeschlossen: {gcm} - {exp} - {var}")
        else:
            print(f"-> FEHLGESCHLAGEN (Exit-Code: {child.exitstatus}): {gcm} - {exp} - {var}. Siehe Log: {log_file_path}")

    except pexpect.TIMEOUT:
        print(f"-> TIMEOUT bei {gcm} - {exp} - {var}. Siehe Log: {log_file_path}")
    except Exception as e:
        print(f"-> Ein FEHLER ist aufgetreten bei {gcm} - {exp} - {var}: {e}")

# ======================================================================
# <<< GEÄNDERT: Hauptteil zur automatischen Erfassung der Aufgaben >>>
# ======================================================================
if __name__ == "__main__":
    
    print("Starte automatische Erfassung der Download-Aufgaben...")
    jobs_to_run = []
    
    # Durchsuche das Quellverzeichnis nach Ordnern, die von Skript 3 erstellt wurden
    for dirname in os.listdir(script_source_dir):
        dir_path = os.path.join(script_source_dir, dirname)
        if os.path.isdir(dir_path):
            # Parse den Ordnernamen, z.B. "CNRM-CM6-1-HR.ssp585.Amon"
            parts = dirname.split('.')
            if len(parts) >= 3:
                gcm = parts[0]
                exp = parts[1]
                table_id = '.'.join(parts[2:]) # fängt auch table_ids mit Punkten ab
                
                # Suche in diesem Ordner nach wget_{var}.sh Skripten
                for script_filename in os.listdir(dir_path):
                    match = re.match(r'wget_(pr|tas|ua)\.sh', script_filename)
                    if match:
                        var = match.group(1)
                        job = {'gcm': gcm, 'exp': exp, 'var': var, 'table_id': table_id}
                        jobs_to_run.append(job)
                        print(f"  [+] Aufgabe gefunden: {gcm} - {exp} - {var}")

    if not jobs_to_run:
        print("\nKeine Aufgaben zum Herunterladen gefunden. Alles scheint erledigt zu sein.")
    else:
        # Bestimme die Anzahl der parallelen Prozesse
        num_workers = min(len(jobs_to_run), cpu_count(), 8)
        print(f"\n{len(jobs_to_run)} Download-Aufgaben gefunden. Starte mit {num_workers} parallelen Prozessen...")
        
        # Starte die Downloads parallel mit der dynamisch erstellten Liste
        with Pool(processes=num_workers) as pool:
            pool.map(download_task, jobs_to_run)

    print("\nAlle Download-Aufgaben abgeschlossen.")