"""Overhaul of my Havok library to leverage dataclass fields and annotations for more concise and readable types.

Designed this way, Havok class members are assumed to be tightly packed (with some alignment potentially occurring after
each type in the class hierarchy) and generic pointer/array/tuple wrapper types are indicated using typing annotations
such as `hkArray[hkInt32]`.

When used, these types are used to generate `BinaryStruct` classes with appropriate unpacking/packing functions for each
typed member field, in the context of the file being unpacked (so pointers/fix-ups/object IDs can be resolved).
"""
import typing as tp
from dataclasses import dataclass, field

from soulstruct.havok.types.hk import (
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

    TODO: Some notes.
        - In hk2014, `hkaAnimation` as a whole is 4-byte aligned (its members start at 12 following its
        `hkReferencedObject` parent class), but the `extractedMotion` pointer is 8-byte aligned. So class alignment does
        NOT inherit from the most alignment-restrictive member.
        - This doesn't happen in hk2015 (tagfiles). The `hkaAnimation` class is 16-byte aligned immediately and there's
        no need to align just before `extractedMotion`. So this is probably weirdness occurring in the only Havok
        version where 8-byte pointers intersect with the packfile format.
            - This probably makes sense, because the packfile format does not record 'type alignment' at all, AFAIK.
            So it's possible that NO alignment occurs between the members of parent/child types, and each member is
            instead responsible for its own alignment. In hk2010, pointers and arrays are only 4-byte aligned, so this
            generally doesn't matter, but in hk2014, pointers are 8-byte aligned, so it does.
            - I suspect that it's the same for arrays, since I've noticed that every single child pointer in every
            hk2014 packfile item is aligned to 8 bytes.
        - In summary:
            - In packfiles, each member aligns itself, which can create invisible pad bytes between members WITHIN the
            same class.
            - In tagfiles,
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
