from enum import Enum


class DataType(str, Enum):
    JSON = "JSON"
    CSV = "CSV"
    YAML = "YAML"
