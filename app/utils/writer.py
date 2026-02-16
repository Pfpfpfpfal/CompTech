import csv
import json
from typing import Any
import yaml

from app.schemas.password import Password


def write_passwords(path: str, data: list[dict[str, Any]] | None = None):
    if not data or not data.get("passwords"):
        return
    extension = path.split(".")[-1]
    
    with open(path, "w") as f:
        if extension in ["yaml", "yml"]:
            yaml.dump(data, f)
            # yaml.safe_dump(data, stream=f)
            return
        if extension == "csv":
            keys = data.get("passwords")[0].keys()
            def get_values_csv(data: Password):
                dumped = data
                return [dumped[key] for key in keys]
            csv_writer = csv.writer(f, delimiter=";")
            csv_writer.writerow(keys)
            csv_writer.writerows([get_values_csv(row) for row in data.get("passwords")])
            return
        if extension == "json":
            f.write(json.dumps(data, indent=2))
            return
        raise Exception("Unsupported data type")
