import csv

import yaml

from app.schemas.password import Password, PasswordList


def read_passwords(path: str) -> PasswordList:
    try:
        with open(path, encoding="utf-8") as file:
            extension = path.split(".")[-1].lower()

            if extension == "json":
                raw = file.read()
                if not raw:
                    return PasswordList()
                return PasswordList.model_validate_json(raw)

            if extension in {"yml", "yaml"}:
                data = yaml.safe_load(file)
                return PasswordList.model_validate(data or {"passwords": []})

            if extension == "csv":
                reader = csv.DictReader(file, delimiter=";")
                passwords = [Password.model_validate(row) for row in reader]
                return PasswordList(passwords=passwords)

            raise ValueError(f"Unsupported data type: {extension}")
    except FileNotFoundError:
        return PasswordList()
