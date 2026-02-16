import csv
import yaml

from app.schemas.password import Password, PasswordList


def read_passwords(path: str) -> PasswordList | None:
    try:
        with open(path) as f:
            extension = path.split(".")[-1]
            if extension == "json":
                raw = f.read()
                if not raw:
                    return PasswordList()
                data = PasswordList.model_validate_json(raw)
                return data
            if extension in ["yml", "yaml"]:
                data = yaml.safe_load(f)
                return PasswordList.model_validate(data)
            if extension == "csv":
                csv_reader = csv.reader(f, delimiter=";")
                keys = []
                data = PasswordList()
                for rownum, row in enumerate(csv_reader):
                    if rownum == 0:
                        keys = row
                        continue
                    data.passwords.append(
                        Password.model_validate(
                            {key: row[keynum] for keynum, key in enumerate(keys)}
                        )
                    )
                return data
    except FileNotFoundError:
        return PasswordList()
