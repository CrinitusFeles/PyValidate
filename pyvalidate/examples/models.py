
from pydantic import BaseModel


class Model(BaseModel):
    arg1: list[int]
    arg2: dict[str, str]


class MyModel(BaseModel):
    var1: str
    var2: int
    var3: Model

class JsonModel(BaseModel):
        v1: list[MyModel]
        v2: dict[str, list[int]]
        v3: str
        v4: int
