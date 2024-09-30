"""Overhaul of my Havok library to leverage dataclass fields and annotations for more concise and readable types.

Designed this way, Havok class members are assumed to be tightly packed (with some alignment potentially occurring after
each type in the class hierarchy) and generic pointer/array/tuple wrapper types are indicated using typing annotations
such as `hkArray[hkInt32]`.

When used, these types are used to generate `BinaryStruct` classes with appropriate unpacking/packing functions for each
typed member field, in the context of the file being unpacked (so pointers/fix-ups/object IDs can be resolved).
"""
import typing as tp
from dataclasses import dataclass, field

from soulstruct_havok.types.hk import (
    hk as old_hk,
    TemplateType, TemplateValue,
)


@dataclass(slots=True)
class hk:
    alignment: tp.ClassVar[int] = 0
    byte_size: tp.ClassVar[int] = 0
    tag_type_flags: tp.ClassVar[int] = 0
    __tag_format_flags: tp.ClassVar[int] = 0
    __hsh: tp.ClassVar[int | None] = None  # only used by some types
    __abstract_value: tp.ClassVar[int | None] = None  # only used by some 'Class' types
    __version: tp.ClassVar[int | None] = None  # only used by some 'Class' types
    __real_name: tp.ClassVar[str] = ""  # if different to type (e.g. colons, asterisk, or clashes with a Python type)
    __templates: tp.ClassVar[tuple[TemplateValue | TemplateType, ...]] = ()
    __interfaces: tp.ClassVar[tuple[TemplateValue | TemplateType, ...]] = ()


def convert_hk_type(hk_type: type[old_hk]):
    """Convert a `hk` type to a `dataclass` type with the same members.

    For safety, to ensure that members are being handled appropriately, this will raise an exception if the existing
    member offsets and class alignments are not correct. Once validated, the member offsets and class byte sizes can be
    discarded, and just the alignment kept.

    To go a step further, the alignment could be discarded if it is predictable from the members. Each Havok class
    presumably inherits the alignment of its most alignment-restrictive member (including parent classes). Some
    reminders on that front:
        - `hkArray` members only require 4-byte alignment, even when their pointers are 64-bit. However, when it comes
        time for their data (stored within-object for Packfiles and in their own objects for Tagfiles), the alignment of
        the data type is used.
        - `hkBaseObject` stores a vtable pointer, which could be 32-bit or 64-bit. This class is obviously abstract, so
        its alignment will always be overridden by subclasses, but it will never be less than 4 bytes.
        - `hkReferencedObject`, an abstract child of `hkBaseObject`, adds fields that track the object's reference count
        and memory size/flags, all of which are obviously zero in serialized files. Every pointable Havok class inherits
        from this class.
    I think I'll keep alignment AND byte size for now, since they are genuinely written to the tagfile types section. In
    cases where the alignment or byte size is larger than the packed member size, this Python class generator will add
    a comment below the last member indicating as such.
    """

    lines = [
        f"@dataclass(slots=True, eq=False, repr=False, kw_only=True)",
        f"class {hk_type.__name__}({hk_type.get_immediate_parent()}):",
    ]

    members = []
    for member in hk_type.members:
        if isinstance(member.type, old_hk):
            members.append((member.name, convert_hk_type(member.type)))
        else:
            members.append((member.name, member.type))
    return dataclass(hk_type, slots=True, eq=False, repr=False, kw_only=True, members=members)
