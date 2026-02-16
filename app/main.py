from multiprocessing import Manager, Pool
from pathlib import Path

from app.database.db import DB
from app.enums.data_types import DataType


def import_wrapper(path: str, lock):
    with lock:
        DB.instance().import_data(path=path)


def export_wrapper(data_type: DataType):
    DB.instance().export_data(data_type=data_type)


def get_import_paths() -> list[str]:
    base = Path.cwd()
    paths: list[str] = []
    for extension in ("json", "yaml", "csv"):
        files = sorted(
            base.glob(f"exported*.{extension}"),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )
        if files:
            paths.append(str(files[0]))
    return paths


if __name__ == "__main__":
    paths = get_import_paths()
    if not paths:
        raise FileNotFoundError("No files matching exported*.json/yaml/csv were found.")

    with Manager() as manager:
        lock = manager.Lock()
        with Pool(min(3, len(paths))) as pool:
            pool.starmap(import_wrapper, [(p, lock) for p in paths])
        
    # TODO: Use Lock with Threads
    # TODO: Try threading on python 3.14 with no GIL

    # db.import_data(path="exported_2025-11-08T11:15:06.236706.json")
    # db.import_data(path="exported_2025-11-08T11:15:06.237727.yaml")
    # db.import_data(path="exported_2025-11-08T11:15:06.257253.csv")

    # db.update(password_id=uuid.uuid4(), data=PasswordUpdate(
    #     name="UPDATED"
    # ))
    # db.update(password_id=uuid.UUID("93f160a6-502a-4541-be8e-26c7919bf3e8"), data=PasswordUpdate(
    #     name="Uslugi",
    #     password=generator.password()
    # ))
    # db.delete(password_id=uuid.uuid4())
    # db.delete(password_id=uuid.UUID("55a83415-94d0-4aac-b7cb-8be154390786"))

    # print(db.get(uuid.UUID("93f160a6-502a-4541-be8e-26c7919bf3e8")).otp)

    # TODO: Поисследовать модуль jsondb и попробовать переопределить методы, которые вам покажутся медленными
    # TODO: Попробовать вместо threading использовать asyncio

    # db.export_data()
    # db.export_data(data_type=DataType.YAML) # TODO: Speed up
    # db.export_data(data_type=DataType.YAML) # TODO: Speed up
    # db.export_data(data_type=DataType.CSV)
    # t1 = Thread(target=db.export_data)
    # t2 = Thread(target=db.export_data, kwargs=dict(data_type=DataType.YAML))
    # t3 = Thread(target=db.export_data, kwargs=dict(data_type=DataType.CSV))
    # t4 = Thread(target=db.export_data, kwargs=dict(data_type=DataType.YAML))
    # t5 = Thread(target=db.export_data, kwargs=dict(data_type=DataType.YAML))
    # t6 = Thread(target=db.export_data, kwargs=dict(data_type=DataType.YAML))

    # t1.start()
    # t2.start()
    # t3.start()
    # t4.start()
    # t5.start()
    # t6.start()

    # t1.join()
    # t2.join()
    # t3.join()
    # t4.join()
    # t5.join()
    # t6.join()

    # p1 = Process(target=db.export_data)
    # p2 = Process(target=db.export_data, kwargs=dict(data_type=DataType.YAML))
    # p3 = Process(target=db.export_data, kwargs=dict(data_type=DataType.CSV))
    # p4 = Process(target=db.export_data, kwargs=dict(data_type=DataType.YAML))
    # p5 = Process(target=db.export_data, kwargs=dict(data_type=DataType.YAML))
    # p6 = Process(target=db.export_data, kwargs=dict(data_type=DataType.YAML))

    # p1.start()
    # p2.start()
    # p3.start()
    # p4.start()
    # p5.start()
    # p6.start()

    # p1.join()
    # p2.join()
    # p3.join()
    # p4.join()
    # p5.join()
    # p6.join()
    with Pool(6) as pool:
        pool.map(
            export_wrapper,
            [
                DataType.JSON,
                DataType.YAML,
                DataType.CSV,
                DataType.YAML,
                DataType.YAML,
                DataType.YAML,
            ],
        )

    # def some_task(number):
    #     print(f"Started {number}")
    #     sleep(5)
    #     print(f"Done {number}")
        
        
    # with Pool(6) as pool:
    #     pool.map(some_task, [1, 2, 3, 4, 5, 6])
