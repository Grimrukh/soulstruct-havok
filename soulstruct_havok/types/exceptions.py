from __future__ import annotations

__all__ = ["HavokTypeError", "VersionModuleError", "TypeNotDefinedError", "TypeMatchError"]

import typing as tp

if tp.TYPE_CHECKING:
    from soulstruct_havok.types.base import hk


class HavokTypeError(Exception):
    """Raised by any error caused by missing, invalid, or malformed Havok types."""


class VersionModuleError(HavokTypeError):
    pass


class TypeNotDefinedError(HavokTypeError):
    """Raised when an undefined parent or member is encountered."""


class TypeMatchError(HavokTypeError):
    """Raised when a Python class's information clashes with a new `TypeInfo`."""
    def __init__(self, py_class: tp.Type[hk], field_name: str, py_value, new_value, binary=False):
        if binary:
            super().__init__(
                f"Python type `{py_class.__name__}` has {field_name} = {format(py_value, f'0{35}_b')}, "
                f"but this `TypeInfo` has {field_name} = {format(new_value, f'0{35}_b')}."
            )
        else:
            super().__init__(
                f"Python type `{py_class.__name__}` has {field_name} = {py_value}, but this `TypeInfo` has "
                f"{field_name} = {new_value}."
            )
