import os
import zipfile
from datetime import datetime

def create_results_zip(base_dir="."):
    """
    Crée une archive ZIP contenant tous les résultats CSV/JSON
    et la place dans le dossier output/archives/
    """

    # Dossier de sortie organisé
    archive_dir = os.path.join(base_dir, "output", "archives")
    os.makedirs(archive_dir, exist_ok=True)

    # Horodatage
    timestamp = datetime.now().strftime("%Y-%m-%d_%Hh%Mmin%Ss")
    zip_name = f"resultats_prevision_{timestamp}.zip"
    zip_path = os.path.join(archive_dir, zip_name)

    # On cherche les fichiers CSV et JSON dans le dossier principal
    for_export = [
        f for f in os.listdir(base_dir)
        if f.endswith(".csv") or f.endswith(".json")
    ]

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
        for f in for_export:
            full_path = os.path.join(base_dir, f)
            z.write(full_path, arcname=f)

    return zip_path
