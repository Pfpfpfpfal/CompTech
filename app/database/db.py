import asyncio
from copy import deepcopy
from datetime import datetime
from typing import Any, Callable
import uuid

import jsondb

from app.enums.data_types import DataType
from app.schemas.password import Password, PasswordUpdate
from app.settings import DATA_PATH
from app.utils.reader import read_passwords
from app.utils.writer import write_passwords


class MyJsonDB(jsondb.JsonDB):
    def ensure_table(self, table_name: str) -> None:
        if self.table_exists(table_name):
            return
        self._data[table_name] = []
        self._save()

    def get_one(self, table_name: str, condition: Callable[[dict[str, Any]], bool]) -> dict[str, Any] | None:
        data = self.get_data(table_name)
        if not isinstance(data, list):
            return None
        item = next((row for row in data if condition(row)), None)
        return deepcopy(item)

    def append_many(self, table_name: str, items: list[dict[str, Any]]) -> None:
        self.ensure_table(table_name)
        data = self.get_data(table_name)
        if not isinstance(data, list):
            raise TypeError(f"Table '{table_name}' is not a list")
        data.extend(items)
        self._data[table_name] = data
        self._save()


class DB:
    _instance: "DB | None" = None

    @classmethod
    def instance(cls) -> "DB":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(self) -> None:
        self._db = MyJsonDB(file_path=DATA_PATH)
        self._db.ensure_table("passwords")

    @staticmethod
    def _same_password_id(password_id: uuid.UUID, row: dict[str, Any]) -> bool:
        return row.get("password_id") == str(password_id)

    @property
    def data(self) -> dict[str, Any]:
        data = self._db.get_data()
        if isinstance(data, dict):
            return data
        return {"passwords": []}

    def insert(self, data: Password) -> Password:
        self._db.append_many("passwords", [data.model_dump(mode="json")])
        return data

    def get(self, password_id: uuid.UUID) -> Password | None:
        row = self._db.get_one("passwords", lambda item: self._same_password_id(password_id, item))
        if row is None:
            return None
        return Password.model_validate(row)

    def update(self, password_id: uuid.UUID, data: PasswordUpdate) -> Password | None:
        current = self.get(password_id)
        if current is None:
            return None

        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(current, key, value)

        self._db.update_data(
            "passwords",
            new_data=current.model_dump(mode="json"),
            condition=lambda item: self._same_password_id(password_id, item),
        )
        return current

    def delete(self, password_id: uuid.UUID) -> Password | None:
        current = self.get(password_id)
        if current is None:
            return None

        self._db.delete_data("passwords", condition=lambda item: self._same_password_id(password_id, item))
        return current

    def export_data(self, data_type: DataType = DataType.JSON) -> str:
        extension = {
            DataType.JSON: "json",
            DataType.YAML: "yaml",
            DataType.CSV: "csv",
        }.get(data_type, "json")

        timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S.%f")
        path = f"exported_{timestamp}.{extension}"
        write_passwords(path, self.data)
        return path

    def import_data(self, path: str) -> int:
        async def dump_password(password: Password) -> dict[str, Any]:
            return password.model_dump(mode="json")

        async def dump_passwords() -> list[dict[str, Any]]:
            password_list = read_passwords(path)
            tasks = [dump_password(password) for password in password_list.passwords]
            return await asyncio.gather(*tasks)

        rows = asyncio.run(dump_passwords())
        if not rows:
            return 0
        self._db.append_many("passwords", rows)
        return len(rows)
