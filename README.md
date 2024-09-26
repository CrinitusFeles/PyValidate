# PyValidate
Python function input data validation by creation dynamic pydantic model based on the annotation of the function argument types


## Installation

```
pip install git+https://github.com/CrinitusFeles/PyValidate
```

or

```
poetry add git+https://github.com/CrinitusFeles/PyValidate
```

## Usage

```python
from pydantic import BaseModel, ValidationError
from pyvalidate import validate_json, validate_args, create_dyn_model


class Model(BaseModel):
    arg1: list[int]
    arg2: dict[str, str]


class MyModel(BaseModel):
    var1: str
    var2: int
    var3: Model


@validate_json
def foo(v1: list[MyModel], v2: dict[str, list[int]], v3: str, v4: int) -> None:
    print(f'{v1[0].model_dump()}, {v2}, {v3}, {v4}\n')

@validate_args
def bar(v1: list[MyModel], v2: dict[str, list[int]], v3: str, v4: int) -> None:
    print(f'{v1[0].model_dump()}, {v2}, {v3}, {v4}\n')


def fn(v1: list[MyModel], v2: dict[str, list[int]], v3: str, v4: int) -> None:
    print(f'{v1[0].model_dump()}, {v2}, {v3}, {v4}\n')


json_str = """{
    "v1":[{
        "var1":"hello",
        "var2":332,
        "var3":{"arg1":[1,2,3],"arg2":{"kek":"lol"}}
    }],
    "v2":{"key_1":[3,2,1],"key_2":[6]},
    "v3":"world","v4":0}
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
```

outpuut:

```
{'var1': 'hello', 'var2': 332, 'var3': {'arg1': [1, 2, 3], 'arg2': {'kek': 'lol'}}}, {'key_1': [3, 2, 1], 'key_2': [6]}, world, 0

{'var1': 'hello', 'var2': 332, 'var3': {'arg1': [1, 2, 3], 'arg2': {'kek': 'lol'}}}, {'kek': [1, 2, 3]}, hello, 123

{'var1': 'hello', 'var2': 332, 'var3': {'arg1': [1, 2, 3], 'arg2': {'kek': 'lol'}}}, {'key_1': [3, 2, 1], 'key_2': [6]}, world, 0

'dict' object has no attribute 'model_dump'
```

If you make incorrect input data like this:
```
json_str = """{
    "v1":[{
        "var1":"hello",
        "var2":332,
        "var3":{"arg1":[1,"a",3],"arg2":{"kek":"lol"}}
    }],
    "v2":{"key_1":[3,2,1],"key_2":[6]},
    "v3":123,"v4":0}
"""
```
(v3 not str and arg1 has string value in list of int)

You will get next result:

```
check_json_validate error:
[{"type":"int_parsing","loc":["v1",0,"var3","arg1",1],"msg":"Input should be a valid integer, unable to parse string as an integer","input":"a"},{"type":"string_type","loc":["v3"],"msg":"Input should be a valid string","input":123}]

{'var1': 'hello', 'var2': 332, 'var3': {'arg1': [1, 2, 3], 'arg2': {'kek': 'lol'}}}, {'kek': [1, 2, 3]}, hello, 123

without_decorator error:
[{"type":"int_parsing","loc":["v1",0,"var3","arg1",1],"msg":"Input should be a valid integer, unable to parse string as an integer","input":"a"},{"type":"string_type","loc":["v3"],"msg":"Input should be a valid string","input":123}]

without_validator error:
'dict' object has no attribute 'model_dump
```