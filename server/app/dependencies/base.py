from typing import ClassVar

from pydantic import BaseModel, Field
from pymilvus.orm.connections import synchronized


class ContextFilter(BaseModel):
    docs_ids: list[str] | None = Field(
        examples=[["c202d5e6-7b69-4869-81cc-dd574ee8ee11"]]
    )


# TODO: This is untested
#  not even sure this is really a singleton
class SingletonMetaClass(type):
    _instances: ClassVar[dict] = {}

    def __init__(cls, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

    def __call__(cls):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__()
        return cls._instances[cls]

    @synchronized
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls, *args, **kwargs)
