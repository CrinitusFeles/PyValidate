from functools import partial, wraps
from typing import Any, Callable, Type, get_type_hints
from types import GenericAlias
from pydantic import BaseModel, create_model  # noqa: F401
from uuid import UUID  # noqa: F401


def expand_generic_alias(alias: GenericAlias) -> str:
    type_repr: str = f'{alias.__name__}['
    args: list[str] = [expand_generic_alias(arg)
                       if isinstance(arg, GenericAlias)
                       else arg.__name__ for arg in alias.__args__]
    if len(args) > 1:
        type_repr += ', '.join(args)
    else:
        type_repr += args[0]
    type_repr += ']'
    return type_repr


def extract_models(type_hints: dict) -> dict[str, type[BaseModel]]:
    def _extract_models(type_val: GenericAlias) -> dict[str, Type[BaseModel]]:
        data: dict[str, type[BaseModel]] = {}
        for arg in type_val.__args__:
            if isinstance(arg, GenericAlias):
                arg_result: dict[str, type[BaseModel]] = _extract_models(arg)
                if len(arg_result):
                    data.update({arg.__name__: arg_result})
            elif issubclass(arg, BaseModel):
                data.update({arg.__name__: arg})
        return data

    data: dict[str, Type[BaseModel]] = {}
    for type_val in type_hints.values():
        if isinstance(type_val, GenericAlias):
            data.update(_extract_models(type_val))
        elif issubclass(type_val, BaseModel):
            data.update({type_val.__name__: type_val})
    return data


def create_model_schema(type_hints: dict) -> str:
    schema: str = ', '.join([f'{key}=({expand_generic_alias(val)}, ...)'
                             if isinstance(val, GenericAlias)
                             else f'{key}=({val.__name__}, ...)'
                             for key, val in type_hints.items()])
    return schema


def _get_type_hints(handler: Callable | partial) -> dict[str, Any]:
    if isinstance(handler, partial):
        type_hints: dict = get_type_hints(handler.func)
    else:
        type_hints = get_type_hints(handler)
    type_hints.pop('return', None)
    type_hints.pop('self', None)
    return type_hints


def create_dyn_model(handler: Callable | partial) -> Type[BaseModel]:
    type_hints: dict[str, Any] = _get_type_hints(handler)
    schema: str = create_model_schema(type_hints)
    data: dict[str, type[BaseModel]] = extract_models(type_hints)
    exec(f"model = create_model('DynamicModel', {schema})", globals(), data)
    return data['model']


def args_to_kwargs(handler: Callable | partial, *args) -> dict[str, Any]:
    type_hints: dict[str, Any] = _get_type_hints(handler)
    kwargs: dict = {key: args[i] for i, key in enumerate(type_hints.keys())}
    return kwargs


def validate_json(func: Callable):
    @wraps(func)
    def wrapper(json_str: str):
        dyn_model: type[BaseModel] = create_dyn_model(func)
        model_dict: dict = dyn_model.model_validate_json(json_str).__dict__
        return func(**model_dict)
    return wrapper


def validate_args(func: Callable):
    @wraps(func)
    def wrapper(*args, **kwargs):
        dyn_model: type[BaseModel] = create_dyn_model(func)
        arg_names = list(_get_type_hints(func).keys())
        func_input: dict[str, Any] = {}
        if len(args) > 0:
            func_input = {arg_names[i]: arg for i, arg in enumerate(args)}
        func_input.update(**kwargs)
        model_dict: dict = dyn_model.model_validate(func_input).__dict__
        return func(**model_dict)
    return wrapper

if __name__ == '__main__':
    print(issubclass(str, BaseModel))