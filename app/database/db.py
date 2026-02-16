import asyncio
import copy
from datetime import datetime
from typing import Any, Callable
import uuid

import jsondb

from app.enums.data_types import DataType
from app.schemas.password import Password, PasswordList, PasswordUpdate
from app.settings import DATA_PATH
from app.utils.reader import read_passwords
from app.utils.writer import write_passwords


class MyJsonDB(jsondb.JsonDB):
    def __insert_into(self, data: list[dict[str, Any]], new_items: list[dict[str, Any]]) -> Any:
        if not isinstance(new_items, list):
            raise jsondb.exceptions.InvalidOperationError(
                f"Cannot insert into data of type '{type(data).__name__}'. "
                f"Only list appends and dict updates are supported."
            )
        new_table = data.copy()
        new_table.extend(new_items)
        return new_table
    
    def get_data(self, table_name: str = None, condition: Callable | None = None) -> Any:
        if not table_name:
            return super().get_data()
        if not condition:
            return super().get_data(table_name)
        obj = next((data for data in self._data[table_name] if condition(data)), None)
        if not obj:
            return None
        return copy.deepcopy(obj)
        
    
    def insert_data(self, table_name: str, data: list[dict[str, Any]] | dict[str, Any]):
        if isinstance(data, dict):
            super().insert_data(table_name=table_name, data=data)
            return
        
        if not self.table_exists(table_name):
            self._data[table_name] = []

        table = self.get_data(table_name) or []
        if not isinstance(table, list):
            raise jsondb.exceptions.InvalidOperationError(
                f"Cannot insert list data into table '{table_name}' of type '{type(table).__name__}'."
            )

        self._data[table_name] = self.__insert_into(table, data)
        self._save()
        

class DB:
    __instance = None
    
    @staticmethod
    def instance():
        if not DB.__instance:
            DB.__instance = DB()
            DB.__instance._load()
        return DB.__instance
    
    def __init__(self):
        self.__db: MyJsonDB | None = None
    
    def _load(self):
        self.__db = MyJsonDB(file_path=DATA_PATH)
        
    def __check(self, password_id: uuid.UUID, structure: list[dict[str, Any]] | dict[str, Any]) -> dict[str, Any] | None:
        if structure.get("password_id") == str(password_id):
            return structure
        return None
        
    def insert(self, data: Password) -> Password:
        self.__db.insert_data("passwords", data=data.model_dump(mode="json"))
    
    @property    
    def __data(self) -> Any:
        data = self.__db.get_data()
        return data
        
    def get(self, password_id: uuid.UUID) -> Password | None:
        db_object = self.__db.get_data("passwords", condition=lambda password: self.__check(password_id=password_id, structure=password))
        if db_object:
            return Password.model_validate(db_object)
        return None
        
    def update(self, password_id: uuid.UUID, data: PasswordUpdate) -> Password | None:
        update_pass = self.get(password_id=password_id)
        if not update_pass:
            return None
        for key, value in data.model_dump(exclude_unset=True).items():
            setattr(update_pass, key, value)
        self.__db.update_data("passwords", new_data=update_pass.model_dump(mode="json"), condition=lambda password: self.__check(password_id=password_id, structure=password))
        return update_pass
        
    def delete(self, password_id: uuid.UUID) -> Password | None:
        delete_pass = self.get(password_id=password_id)
        if not delete_pass:
            return None
        self.__db.delete_data("passwords", condition=lambda password: self.__check(password_id=password_id, structure=password))
        return delete_pass
    
    def export_data(self, data_type: DataType | None = DataType.JSON):
        extension = {
            DataType.JSON: "json",
            DataType.YAML: "yaml",
            DataType.CSV: "csv"
        }.get(data_type, "unknown")
        # Windows does not allow ":" in file names.
        timestamp = datetime.now().strftime("%Y-%m-%dT%H-%M-%S.%f")
        write_passwords(
            f"exported_{timestamp}.{extension}",
            self.__data
        )
        
    def import_data(self, path: str):
        async def dump_password(password: Password) -> dict[str, Any]:
            return password.model_dump(mode="json")
        
        async def dump_passwords() -> list[dict[str, Any]]:
            coros = [dump_password(password) for password in read_passwords(path=path).passwords]
            return await asyncio.gather(*coros)
        
        self.__db.insert_data("passwords", data=asyncio.run(dump_passwords()))
