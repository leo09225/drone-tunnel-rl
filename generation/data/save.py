import csv
from datetime import datetime
from pathlib import Path


def _get_method_folder_name(method):
    if method is None:
        return None

    normalized_method = str(method).strip().lower()

    if normalized_method == "ca":
        return "CA"

    if normalized_method == "agent":
        return "agent"

    return normalized_method or None


def _build_unique_file_path(folder_path, n, m):
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    base_name = f"{n}x{m}_matrix_{timestamp}"
    file_path = folder_path / f"{base_name}.csv"
    suffix = 1

    while file_path.exists():
        file_path = folder_path / f"{base_name}_{suffix}.csv"
        suffix += 1

    return file_path


def save_matrix_to_csv(matrix, n, m, start_position=None, method=None):
    """
    Sauvegarde la matrice dans un fichier CSV dans le dossier correspondant à ses
    dimensions. Si une méthode est fournie, un sous-dossier dédié est créé
    (`CA` ou `agent`). La première ligne contient la position du départ au
    format [colonne, ligne, ...] pour rester compatible avec le module
    multi_agent.
    """
    base_dir = Path(__file__).resolve().parent
    folder_path = base_dir / f"{n}X{m}"
    method_folder_name = _get_method_folder_name(method)

    if method_folder_name is not None:
        folder_path = folder_path / method_folder_name

    folder_path.mkdir(parents=True, exist_ok=True)

    file_path = _build_unique_file_path(folder_path, n, m)

    with file_path.open(mode="w", newline="") as file:
        writer = csv.writer(file)
        row_width = len(matrix[0]) if matrix else 0

        if start_position is None:
            header = ["", ""] + [""] * max(row_width - 2, 0)
        else:
            start_column, start_row = start_position
            header = [start_column, start_row] + [""] * max(row_width - 2, 0)

        writer.writerow(header)
        writer.writerows(matrix)
    print(f"[INFO] Matrice enregistree : {file_path}")
    return file_path
