from multiprocessing import Manager, Pool
from pathlib import Path

from app.database.db import DB
from app.enums.data_types import DataType


def import_wrapper(path: str, lock) -> tuple[str, int]:
    with lock:
        imported = DB.instance().import_data(path)
    return path, imported


def export_wrapper(data_type: DataType) -> tuple[DataType, str]:
    output_path = DB.instance().export_data(data_type=data_type)
    return data_type, output_path


def get_import_paths() -> list[str]:
    base = Path.cwd()
    paths: list[str] = []
    for extension in ("json", "yaml", "csv"):
        files = sorted(
            base.glob(f"exported*.{extension}"),
            key=lambda file: file.stat().st_mtime,
            reverse=True,
        )
        if files:
            paths.append(str(files[0]))
    return paths


if __name__ == "__main__":
    paths = get_import_paths()
    if not paths:
        print("No input files found: exported*.json/yaml/csv")
    else:
        with Manager() as manager:
            lock = manager.Lock()
            with Pool(min(3, len(paths))) as pool:
                imported_results = pool.starmap(import_wrapper, [(path, lock) for path in paths])
        for path, count in imported_results:
            print(f"Imported {count} records from: {path}")

    export_types = [DataType.JSON, DataType.YAML, DataType.CSV]
    with Pool(len(export_types)) as pool:
        export_results = pool.map(export_wrapper, export_types)
    for data_type, output_path in export_results:
        print(f"Exported {data_type.value.lower()}: {output_path}")
