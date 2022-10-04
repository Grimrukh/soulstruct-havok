from __future__ import annotations

__all__ = ["convert_hk"]

import copy
import typing as tp
from types import ModuleType

from soulstruct_havok.enums import MemberFlags
from soulstruct_havok.types.core import *


class HKConversionError(Exception):
    """Raised when a source member name is not found in the destination object, or vice versa."""


def find_type(types_module: ModuleType, name: str):
    try:
        return getattr(types_module, name)
    except AttributeError:
        # TODO: Not handling this yet. Seems unlikely to be resolvable.
        raise HKConversionError(
            f"Could not find a class named `{name}` in dest types module."
        )


def convert_hk(
    source_object: hk,
    dest_object_type: tp.Type[hk],
    dest_types_module: ModuleType,
    source_error_handler: tp.Callable = None,
    dest_error_handler: tp.Callable = None,
    indent="",
):
    """Recursively convert all member values in `source_object` to an instance of `dest_object_type`.

    This operates by iterating over the members of the class and calling this function again when another `hk` instance
    is found as a member value, passing in the `hk` type detected in that member's information in `dest_object_type`.

    If a member name in `source_object` is not found in `dest_object_type`, an error will be raised and the converter
    will attempt to handle it automatically: the source object's class, the name and value of the member, and the
    in-progress instance of `dest_object_type` will all be passed to `forward_error_handler`. This handler should
    attempt to update the appropriate new members in the dest object, and return a list of new member names affected.
    If it returns an empty list, that will indicate that the handler could not resolve the problem, and the error will
    be raised to the caller (which may be a higher call of this same function, will will attempt to handle the error
    the same way).

    If any member names in `dest_object_type` are not found in `source_object`, and are not in one of the lists
    returned by an `error_handler` call, then an error will be immediately raised (as every member MUST be set to
    something in Python).

    Typically, you will call this on the `hkRootLevelContainer` at the top of the HKX file.

    TODO: `NonSerializable` members should be defaultable (0, None, or empty, I imagine).
    """
    dest_object = dest_object_type()
    dest_object_member_names = dest_object.get_member_names()
    handled_dest_member_names = []

    for member_name in source_object.get_member_names():
        source_member_value = getattr(source_object, member_name)

        if member_name not in dest_object_member_names:
            if source_error_handler:
                handled_names = source_error_handler(source_object, member_name, source_member_value, dest_object)
                if handled_names is not None:  # could be empty (e.g., deleted members)
                    handled_dest_member_names += handled_names
                    continue
                else:
                    raise HKConversionError(
                        f"Error handler could not resolve missing member '{member_name}' for destination object "
                        f"{dest_object_type.__name__}."
                    )
            else:
                raise HKConversionError(
                    f"Cannot find member name '{member_name}' in destination object {dest_object_type.__name__}"
                )

        if isinstance(source_member_value, hk):
            # Find matching class (may be a subclass of documented type for `hk` instances).
            source_member_type = type(source_member_value)  # type: tp.Type[hk]  # could be a subclass
            dest_member_type = find_type(dest_types_module, source_member_type.__name__)
            dest_member_value = convert_hk(
                source_member_value,
                dest_member_type,
                dest_types_module,
                source_error_handler,
                dest_error_handler,
                indent + " " * 4,
            )
        elif isinstance(source_member_value, (list, tuple)):
            source_member_type = source_object.get_member(member_name).type
            if not issubclass(source_member_type, hkBasePointer):
                raise TypeError(
                    f"Expected list/tuple member '{member_name}' type `{source_member_type.__name__}` to be a "
                    f"`hkBasePointer` subclass, but it is not."
                )
            source_member_type: tp.Type[hkBasePointer]

            dest_elements = []
            dest_element_type = None

            for source_element in source_member_value:
                if isinstance(source_element, hk):
                    if dest_element_type is None:  # only needed for first element (which could be a subclass)
                        dest_element_type = find_type(dest_types_module, type(source_element).__name__)
                    dest_element = convert_hk(
                        source_element,
                        dest_element_type,
                        dest_types_module,
                        source_error_handler,
                        dest_error_handler,
                        indent + " " * 4,
                    )
                    dest_elements.append(dest_element)
                elif isinstance(source_element, (list, tuple)):
                    # Assert primitive/empty.
                    if not source_element or isinstance(source_element[0], (float, int)):
                        dest_elements.append(copy.deepcopy(source_element))
                    else:
                        raise NotImplementedError(
                            f"Too lazy to implement conversion for lists/tuples of lists/tuples yet. Source object "
                            f"type {source_object.get_type_name()}, member name {member_name}."
                        )
                else:  # primitive (could still be a class such as `Vector4`, so we copy)
                    dest_elements.append(copy.deepcopy(source_element))

            if isinstance(source_member_value, tuple):
                dest_member_value = tuple(dest_elements)
            else:
                dest_member_value = dest_elements  # list is correct
        else:  # primitive (could still be a class such as `Vector4`, so we copy)
            dest_member_value = copy.deepcopy(source_member_value)

        setattr(dest_object, member_name, dest_member_value)
        handled_dest_member_names.append(member_name)

    # Check that all dest members were handled.
    for dest_member_name in dest_object.get_member_names():
        if dest_member_name not in handled_dest_member_names:
            if dest_error_handler and dest_error_handler(dest_object, dest_member_name):
                continue
            dest_member = dest_object.get_member(dest_member_name)
            if dest_member.extra_flags & MemberFlags.NotSerializable:
                try:
                    default = dest_member.type.get_default_value()
                except ValueError:
                    raise HKConversionError(
                        f"Non-serialized member '{dest_member_name}' of destination `{dest_object.get_type_name()}` "
                        f"was never set and no default value is available."
                    )
                else:
                    setattr(dest_object, dest_member_name, default)
                    continue
            raise HKConversionError(
                f"Serialized member '{dest_member_name}' of destination `{dest_object.get_type_name()}` was never set "
                f"and no default value is available."
            )

    return dest_object