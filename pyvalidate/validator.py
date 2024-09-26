from functools import partial, wraps
import inspect
from typing import Any, Callable, Type, get_type_hints
from types import GenericAlias
from pydantic import BaseModel, create_model  # noqa: F401


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
    return type_hints


def create_dyn_model(handler: Callable | partial,
                     glob: dict | None = None) -> Type[BaseModel]:
    type_hints: dict[str, Any] = _get_type_hints(handler)
    schema: str = create_model_schema(type_hints)
    stack = inspect.stack()
    if not glob:
        glob = stack[1].frame.f_globals
    exec(f"model = create_model('DynamicModel', {schema})", globals(), glob)
    return glob['model']


def validate_json(func: Callable):
    @wraps(func)
    def wrapper(json_str: str):
        glob: dict = inspect.stack()[1].frame.f_globals
        dyn_model: type[BaseModel] = create_dyn_model(func, glob)
        model_dict: dict = dyn_model.model_validate_json(json_str).__dict__
        return func(**model_dict)
    return wrapper


def validate_args(func: Callable):
    @wraps(func)
    def wrapper(*args, **kwargs):
        glob: dict = inspect.stack()[1].frame.f_globals
        dyn_model: type[BaseModel] = create_dyn_model(func, glob)
        arg_names = list(_get_type_hints(func).keys())
        func_input: dict[str, Any] = {}
        if len(args) > 0:
            func_input = {arg_names[i]: arg for i, arg in enumerate(args)}
        func_input.update(**kwargs)
        model_dict: dict = dyn_model.model_validate(func_input).__dict__
        return func(**model_dict)
    return wrapper