import json
from pydantic import BaseModel, ValidationError
from pyvalidate import validate_json, validate_args, create_dyn_model
from pyvalidate.examples.models import JsonModel, Model, MyModel



@validate_json
def foo(v1: list[MyModel], v2: dict[str, list[int]], v3: str, v4: int) -> None:
    print(f'{v1[0].model_dump()}, {v2}, {v3}, {v4}\n')

@validate_args
def bar(v1: list[MyModel], v2: dict[str, list[int]], v3: str, v4: int) -> None:
    print(f'{v1[0].model_dump()}, {v2}, {v3}, {v4}\n')


def fn(v1: list[MyModel], v2: dict[str, list[int]], v3: str, v4: int) -> None:
    print(f'{v1[0].model_dump()}, {v2}, {v3}, {v4}\n')


def get_json() -> str:
    v1 = MyModel(var1='hello', var2=332,
                 var3=Model(arg1=[1, 2, 3], arg2={'kek': 'lol'}))
    model = JsonModel(v1=[v1], v2={'key_1': [3, 2, 1], 'key_2': [6]},
                      v3='world', v4=0)
    return model.model_dump_json()


json_str = """{
    "v1":[{
        "var1":"hello",
        "var2":332,
        "var3":{"arg1":[1,"a",3],"arg2":{"kek":"lol"}}
    }],
    "v2":{"key_1":[3,2,1],"key_2":[6]},
    "v3":123,"v4":0}
"""


def check_json_validate() -> None:
    try:
        foo(json_str)
    except ValidationError as err:
        print(f'check_json_validate error:\n{err.json(include_url=False)}')


def check_args_validate() -> None:
    v1 = MyModel(var1='hello', var2=332,
                 var3=Model(arg1=[1, 2, 3], arg2={'kek': 'lol'}))
    try:
        bar([v1], {'kek': [1, 2, 3]}, 'hello', 123)
    except ValidationError as err:
        print(f'check_args_validate error:\n{err.json(include_url=False)}')


def without_decorator() -> None:
    try:
        dyn_model: type[BaseModel] = create_dyn_model(foo)
        model_dict: dict = dyn_model.model_validate_json(json_str).__dict__
        fn(**model_dict)
    except ValidationError as err:
        print(f'without_decorator error:\n{err.json(include_url=False)}')


def without_validator() -> None:
    try:
        data: dict = json.loads(json_str)
        fn(**data)
    except Exception as err:
        print(f'without_validator error:\n{err}')


if __name__ == '__main__':
    check_json_validate()
    check_args_validate()
    without_decorator()
    without_validator()
