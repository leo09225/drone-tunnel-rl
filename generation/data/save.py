import csv
from pathlib import Path


def save_matrix_to_csv(matrix, n, m):
    """
    Sauvegarde la matrice dans un fichier CSV dans le dossier correspondant à ses dimensions.
    Le dossier est nommé en fonction des dimensions, par exemple '15X30'.
    """
    base_dir = Path(__file__).resolve().parent
    folder_path = base_dir / f"{n}X{m}"
    folder_path.mkdir(parents=True, exist_ok=True)

    file_path = folder_path / f"{n}x{m}_matrix.csv"

    with file_path.open(mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(matrix)
    print(f"Matrix saved to {file_path}")
