import csv
import json
from typing import Any

import yaml


def write_passwords(path: str, data: dict[str, Any] | None = None) -> None:
    if not data or not data.get("passwords"):
        return

    extension = path.split(".")[-1].lower()

    if extension in {"yml", "yaml"}:
        with open(path, "w", encoding="utf-8") as file:
            yaml.safe_dump(data, file, allow_unicode=True)
        return

    if extension == "json":
        with open(path, "w", encoding="utf-8") as file:
            file.write(json.dumps(data, ensure_ascii=False, indent=2))
        return

    if extension == "csv":
        rows = data["passwords"]
        keys = list(rows[0].keys())
        with open(path, "w", encoding="utf-8", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=keys, delimiter=";")
            writer.writeheader()
            writer.writerows(rows)
        return

    raise ValueError(f"Unsupported data type: {extension}")
