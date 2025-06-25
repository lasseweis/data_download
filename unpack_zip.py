import os
import glob
import zipfile
import shutil

# ======================= KONFIGURATION =======================
# Passen Sie diese Pfade an Ihre Umgebung an.

# 1. Quellverzeichnis: Der Ordner, in dem Ihre heruntergeladenen .zip-Dateien liegen.
QUELLE_VERZEICHNIS = "/nas/home/vlw/Desktop/STREAM/data-download-files"

# 2. Zielverzeichnisse: Eine "Karte", die jedem Variablen-Präfix ein Zielverzeichnis zuweist.
ZIEL_MAP = {
    'pr': "/data/users/vlw/paper1-cmip-data/pr",
    'tas': "/data/users/vlw/paper1-cmip-data/tas",
    'ua': "/data/users/vlw/paper1-cmip-data/ua"
}

# 3. Temporäres Verzeichnis: Ein Ordner mit VIEL freiem Speicherplatz für das Entpacken.
TEMP_VERZEICHNIS = "/data/reloclim/normal"  # <-- DIESE ZEILE WAR NÖTIG

# ===================== ENDE DER KONFIGURATION ====================


#                 Parameter hier hinzugefügt -- v
def sortiere_und_entpacke_cmip_daten(quelle, ziel_map, temp_pfad):
    """
    Durchsucht ein Quellverzeichnis nach .zip-Dateien, entpackt die .nc-Dateien
    und sortiert sie basierend auf ihrem Dateinamen in die richtigen Zielordner.
    """
    print(f"Suche nach .zip-Dateien in: '{quelle}'")
    
    zip_dateien = glob.glob(os.path.join(quelle, '*.zip'))

    if not zip_dateien:
        print("Keine .zip-Dateien im Quellverzeichnis gefunden.")
        return

    print(f"{len(zip_dateien)} .zip-Datei(en) gefunden. Beginne mit der Verarbeitung...")
    print("-" * 40)

    # Sicherstellen, dass das Haupt-Temp-Verzeichnis existiert
    os.makedirs(temp_pfad, exist_ok=True)

    for zip_pfad in zip_dateien:
        dateiname = os.path.basename(zip_pfad)
        print(f"Verarbeite: {dateiname}")

        # Temporären Ordner mit dem neuen Parameter 'temp_pfad' erstellen
        temp_ordner = os.path.join(temp_pfad, f"temp_{dateiname[:-4]}") # <-- HIER WIRD DER PARAMETER VERWENDET
        os.makedirs(temp_ordner, exist_ok=True)

        try:
            with zipfile.ZipFile(zip_pfad, 'r') as zip_ref:
                zip_ref.extractall(temp_ordner)

            # (Restlicher Code ist unverändert)
            nc_dateien_gefunden = glob.glob(os.path.join(temp_ordner, '**', '*.nc'), recursive=True)

            if not nc_dateien_gefunden:
                print("  -> Keine .nc-Datei in diesem Archiv gefunden.")
            else:
                for nc_datei_pfad in nc_dateien_gefunden:
                    nc_dateiname = os.path.basename(nc_datei_pfad)
                    ziel_gefunden = False

                    for praefix, ziel_ordner in ziel_map.items():
                        if nc_dateiname.startswith(praefix + '_'):
                            os.makedirs(ziel_ordner, exist_ok=True)
                            ziel_pfad = os.path.join(ziel_ordner, nc_dateiname)
                            shutil.move(nc_datei_pfad, ziel_pfad)
                            print(f"  -> Datei '{nc_dateiname}' nach '{ziel_ordner}' verschoben.")
                            ziel_gefunden = True
                            break
                    
                    if not ziel_gefunden:
                        print(f"  -> WARNUNG: Kein Zielverzeichnis für '{nc_dateiname}' gefunden. Datei wird ignoriert.")

        except zipfile.BadZipFile:
            print(f"  -> FEHLER: '{dateiname}' ist eine ungültige ZIP-Datei.")
        
        finally:
            if os.path.exists(temp_ordner):
                shutil.rmtree(temp_ordner)
            os.remove(zip_pfad)
            print(f"  -> Aufräumen abgeschlossen für '{dateiname}'.")
            print("-" * 40)

    print("Alle Aufgaben erledigt.")

# Das Skript ausführen
if __name__ == "__main__":
    # Die Funktion jetzt mit drei Argumenten aufrufen
    sortiere_und_entpacke_cmip_daten(QUELLE_VERZEICHNIS, ZIEL_MAP, TEMP_VERZEICHNIS) # <-- DRITTES ARGUMENT HINZUGEFÜGT