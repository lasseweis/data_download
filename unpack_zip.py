import os
import glob
import zipfile
import shutil

# ======================= KONFIGURATION =======================
# Passen Sie diese Pfade an Ihre Umgebung an.

# 1. Quellverzeichnis: Der Ordner, in dem Ihre heruntergeladenen .zip-Dateien liegen.
QUELLE_VERZEICHNIS = "/data/users/vlw/paper1-cmip-data/downloads"  # <-- BITTE ANPASSEN

# 2. Zielverzeichnisse: Eine "Karte", die jedem Variablen-Präfix ein Zielverzeichnis zuweist.
#    Sie können diese Liste einfach erweitern, z.B. 'hus': '/pfad/zu/hus'
ZIEL_MAP = {
    'pr': "/data/users/vlw/paper1-cmip-data/pr",
    'tas': "/data/users/vlw/paper1-cmip-data/tas",
    'ua': "/data/users/vlw/paper1-cmip-data/ua"
}

# ===================== ENDE DER KONFIGURATION ====================


def sortiere_und_entpacke_cmip_daten(quelle, ziel_map):
    """
    Durchsucht ein Quellverzeichnis nach .zip-Dateien, entpackt die .nc-Dateien
    und sortiert sie basierend auf ihrem Dateinamen in die richtigen Zielordner.
    """
    print(f"Suche nach .zip-Dateien in: '{quelle}'")
    
    # Finde alle .zip-Dateien im Quellverzeichnis
    zip_dateien = glob.glob(os.path.join(quelle, '*.zip'))

    if not zip_dateien:
        print("Keine .zip-Dateien im Quellverzeichnis gefunden.")
        return

    print(f"{len(zip_dateien)} .zip-Datei(en) gefunden. Beginne mit der Verarbeitung...")
    print("-" * 40)

    for zip_pfad in zip_dateien:
        dateiname = os.path.basename(zip_pfad)
        print(f"Verarbeite: {dateiname}")

        # Temporären Ordner im Quellverzeichnis erstellen
        temp_ordner = os.path.join(quelle, f"temp_{dateiname[:-4]}")
        os.makedirs(temp_ordner, exist_ok=True)

        try:
            with zipfile.ZipFile(zip_pfad, 'r') as zip_ref:
                zip_ref.extractall(temp_ordner)

            # Suche nach allen .nc-Dateien im temporären Ordner
            nc_dateien_gefunden = glob.glob(os.path.join(temp_ordner, '**', '*.nc'), recursive=True)

            if not nc_dateien_gefunden:
                print("  -> Keine .nc-Datei in diesem Archiv gefunden.")
            else:
                for nc_datei_pfad in nc_dateien_gefunden:
                    nc_dateiname = os.path.basename(nc_datei_pfad)
                    ziel_gefunden = False

                    # Finde das richtige Zielverzeichnis anhand des Präfixes
                    for praefix, ziel_ordner in ziel_map.items():
                        if nc_dateiname.startswith(praefix + '_'):
                            # Sicherstellen, dass der Zielordner existiert
                            os.makedirs(ziel_ordner, exist_ok=True)
                            
                            # Zielpfad für die Datei erstellen und dorthin verschieben
                            ziel_pfad = os.path.join(ziel_ordner, nc_dateiname)
                            shutil.move(nc_datei_pfad, ziel_pfad)
                            print(f"  -> Datei '{nc_dateiname}' nach '{ziel_ordner}' verschoben.")
                            ziel_gefunden = True
                            break  # Nächste .nc-Datei bearbeiten
                    
                    if not ziel_gefunden:
                        print(f"  -> WARNUNG: Kein Zielverzeichnis für '{nc_dateiname}' gefunden. Datei wird ignoriert.")

        except zipfile.BadZipFile:
            print(f"  -> FEHLER: '{dateiname}' ist eine ungültige ZIP-Datei.")
        
        finally:
            # Räume den temporären Ordner und die .zip-Datei auf
            if os.path.exists(temp_ordner):
                shutil.rmtree(temp_ordner)
            os.remove(zip_pfad)
            print(f"  -> Aufräumen abgeschlossen für '{dateiname}'.")
            print("-" * 40)

    print("Alle Aufgaben erledigt.")

# Das Skript ausführen
if __name__ == "__main__":
    sortiere_und_entpacke_cmip_daten(QUELLE_VERZEICHNIS, ZIEL_MAP)