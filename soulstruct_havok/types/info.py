"""Classes for representing direct information about a Havok type unpacked from, or to be packed to, a file."""
from __future__ import annotations

__all__ = [
    "HAVOK_TYPE_PREFIXES",
    "TemplateInfo",
    "MemberInfo",
    "InterfaceInfo",
    "TypeInfo",
    "get_py_name",
]

import typing as tp
from dataclasses import dataclass, field

from soulstruct_havok.enums import TagDataType, TagFormatFlags, MemberFlags

from .exceptions import TypeMatchError
from .py_def_builder import PyDefBuilder

if tp.TYPE_CHECKING:
    from .hk import hk


# Any type whose real Havok name does not start with one of these will have an underscore prepended to its Python name.
# (The 'Custom' prefix is for at least one FromSoftware mesh subtype.)
HAVOK_TYPE_PREFIXES = ("hk", "hcl", "Custom")


def get_py_name(real_name: str) -> str:
    py_name = real_name.replace("T*", "Ptr").replace("::", "").replace(" ", "_").replace("*", "STAR")
    if not any(py_name.startswith(s) for s in HAVOK_TYPE_PREFIXES) and not py_name.startswith("Ptr"):
        py_name = "_" + py_name  # for 'int', 'const_charSTAR', etc.
    return py_name


@dataclass(slots=True, repr=False)
class TemplateInfo:
    """Simple container for an unpacked template name and value."""
    name: str
    value: None | int = -1  # will be a type index if name starts with 't'

    type_info: None | TypeInfo = None
    type_py_name: None | str = None

    def indexify(self, type_py_names: list[str]):
        if self.name.startswith("t"):
            self.value = type_py_names.index(self.type_py_name)
        # Otherwise, do nothing ('v' template).

    @property
    def is_type(self):
        return self.name.startswith("t")

    @property
    def is_value(self):
        return self.name.startswith("v")

    def __repr__(self):
        if self.is_type:
            return f"TemplateInfo(\"{self.name}\", <{self.type_info.name if self.type_info else None}>)"
        return f"TemplateInfo(\"{self.name}\", {self.value})"


@dataclass(slots=True, repr=False)
class MemberInfo:
    """Simple container for information about a specific member of a single type."""
    name: str
    flags: int
    offset: int

    type_index: int | None = None
    type_info: TypeInfo | None = None
    type_py_name: str | None = None

    # Attributes used temporaneously by Python auto-generator.
    member_py_name: str | None = None
    type_hint: str | None = None
    required_types: list[str] = field(default_factory=list)

    def indexify(self, type_py_names: list[str]):
        try:
            self.type_index = type_py_names.index(self.type_py_name)
        except ValueError:
            raise ValueError(f"Could not find {self.type_py_name} in types (member \"{self.name}\")")

    def deindexify(self, type_infos: list[TypeInfo]):
        try:
            self.type_info = type_infos[self.type_index]
        except ValueError:
            raise ValueError(f"Could not assign `TypeInfo` of member '{self.name}' (type index {self.type_index}).")
        self.type_py_name = self.type_info.py_name

    def get_tag_member_flags_repr(self, exclude_default=True) -> str:
        """Get a bitwise-OR combination of `MemberFlags` values."""
        if self.flags == MemberFlags.Default:
            return "MemberFlags.Default"
        string = ""
        remaining_flags = self.flags
        if exclude_default:
            remaining_flags -= MemberFlags.Default
        for flag in MemberFlags:
            if (not exclude_default or flag != MemberFlags.Default) and self.flags & flag:
                if string:
                    string += " | "
                string += f"MemberFlags.{flag.name}"
                remaining_flags -= flag
        if remaining_flags:
            raise ValueError(f"Unknown member flags detected: {self.flags}")
        return string

    def __repr__(self):
        return (
            f"MemberInfo(\"{self.name}\" | {self.member_py_name}, {self.type_py_name} <{self.type_index}>, "
            f"flags={self.flags}, offset={self.offset})"
        )


@dataclass(slots=True, repr=False)
class InterfaceInfo:
    """Simple container for information about an interface of a single type."""
    flags: int

    type_index: int | None = None
    type_info: TypeInfo | None = None
    type_py_name: str | None = None

    def indexify(self, type_py_names: list[str]):
        self.type_index = type_py_names.index(self.type_py_name)

    def __repr__(self):
        return f"InterfaceInfo({self.flags}, <{self.type_py_name}>)"


@dataclass(slots=True, repr=False)
class TypeInfo:
    """Holds information about a type, temporarily. Designed to correspond 1-for-1 with types unpacked from tagfiles,
    including all generic types like hkArray, T*, T[N], etc.

    Initialized first with just name and template (from "TNAM" section), then remaining info later. Only used to compare
    against known types, and to help add to those known types if new.
    """

    GENERIC_TYPE_NAMES: tp.ClassVar[list[str]] = [
        "hkArray", "hkEnum", "hkRefPtr", "hkRefVariant", "hkViewPtr", "T*", "T[N]", "hkRelArray", "hkFlags",
        "hkFreeListArray", "hkFreeListArrayElement",
    ]

    _PY_DEF_HEADER: tp.ClassVar[str] = (
        "from __future__ import annotations\n\n"
        "from soulstruct_havok.types.core import *\n"
        "from soulstruct_havok.enums import *\n"
        "from .core import *\n\n\n"
    )

    name: str

    templates: list[TemplateInfo] = field(default_factory=list)
    parent_type_index: int | None = None
    tag_format_flags: int | None = None
    tag_type_flags: int | None = None
    pointer_type_index: int | None = None
    version: int | None = None
    byte_size: int | None = None
    alignment: int | None = None
    abstract_value: int | None = None
    members: list[MemberInfo] = field(default_factory=list)
    interfaces: list[InterfaceInfo] = field(default_factory=list)
    hsh: int | None = None

    parent_type_info: TypeInfo | None = None
    parent_type_py_name: str | None = None
    pointer_type_info: TypeInfo | None = None
    pointer_type_py_name: str | None = None

    py_class: tp.Type[hk] | None = None

    def indexify(self, type_py_names: list[str]):
        """Use `type_py_names` indices and `self.py_class`, if present, to fill in indices.

        `type_py_names` will be padded at the front with an empty string to allow easy retrieval of 1-indices.
        """
        for template in self.templates:
            template.indexify(type_py_names)

        if self.parent_type_py_name is not None:
            self.parent_type_index = type_py_names.index(self.parent_type_py_name)
        else:
            self.parent_type_index = 0

        if self.pointer_type_py_name is not None:
            self.pointer_type_index = type_py_names.index(self.pointer_type_py_name)
        else:
            self.pointer_type_index = 0

        for member in self.members:
            try:
                member.indexify(type_py_names)
            except ValueError as ex:
                raise ValueError(f"Error indexifying members of {self.name}: {ex}")

        for interface in self.interfaces:
            interface.indexify(type_py_names)

    def get_member_info(self, name: str) -> MemberInfo:
        for member in self.members:
            if member.name == name:
                return member
        raise ValueError(f"Could not find member with name '{name}' in `TypeInfo` '{self.name}'.")

    def get_parent_value(self, field_name: str):
        """Iterate up parent types until a non-zero value for `field_name` is found."""
        child_value = getattr(self, field_name)
        if child_value is not None:
            return child_value
        if self.parent_type_info is None:
            raise ValueError(f"No parent to check for `TypeInfo` {self.name} to retrieve \"{field_name}\".")
        return self.parent_type_info.get_parent_value(field_name)

    @property
    def tag_data_type(self) -> tp.Optional[TagDataType]:
        """From lowest byte of `tag_type_flags`.

        Returns `None` if type flags are absent (e.g., Havok aliases like `hkUint16`).
        """
        if self.tag_type_flags is None:
            return None
        return TagDataType(self.tag_type_flags & 0xFF)

    def get_tag_type_flags_repr(self) -> str:
        """Get a bitwise-OR combination of `TagDataType` values."""
        data_type = self.tag_data_type
        if data_type == TagDataType.Struct:
            struct_length = (self.tag_type_flags & 0xFFFFFF00) >> 8
            return f"TagDataType.{data_type.name} | {struct_length} << 8"
        elif data_type == TagDataType.Int:
            is_signed = TagDataType(self.tag_type_flags & 0x200)
            int_size = TagDataType(self.tag_type_flags & 0xFFFFFC00)
            if int_size != TagDataType.Void:
                if is_signed:
                    return f"TagDataType.{data_type.name} | TagDataType.{is_signed.name} | TagDataType.{int_size.name}"
                return f"TagDataType.{data_type.name} | TagDataType.{int_size.name}"
            return f"TagDataType.{data_type.name}"
        data_sub_type = TagDataType(self.tag_type_flags & 0xFFFFFF00)
        if not data_sub_type:
            return f"TagDataType.{data_type.name}"
        return f"TagDataType.{data_type.name} | TagDataType.{data_sub_type.name}"

    @property
    def py_name(self) -> str:
        return get_py_name(self.name)

    def get_full_py_name(self) -> str:
        """Get actual generic type, if appropriate, eg `hkArray[Ptr[hkaAnimation]]`."""
        name = self.py_name

        if self.tag_format_flags & TagFormatFlags.Pointer:
            if self.pointer_type_info:
                return f"{name}[{self.pointer_type_info.get_full_py_name()}]"
            elif self.pointer_type_py_name:
                return f"{name}[{self.pointer_type_py_name}]"
        return name

    def check_py_class_match(self, py_class: tp.Type[hk]) -> dict[str, int]:
        """Check `TypeInfo` attributes (typically from a file) against attributes of pre-defined Python class.

        Raises a `TypeMatchError` if a clash occurs, and does nothing otherwise.
        """
        changes = {}

        if self.parent_type_py_name is not None:
            py_parent_name = py_class.__bases__[-1].__name__
            if self.parent_type_py_name != py_parent_name:
                raise TypeMatchError(py_class, "parent", py_parent_name, self.parent_type_py_name)
        for field_name in ("tag_type_flags", "byte_size", "alignment"):
            py_value = getattr(py_class, field_name)
            new_value = self.get_parent_value(field_name)
            if py_value != new_value:
                raise TypeMatchError(py_class, field_name, py_value, new_value, binary=field_name == "tag_type_flags")
        for non_inherited_field in ("tag_format_flags", "hsh", "abstract_value", "version"):
            py_value = getattr(py_class, f"get_{non_inherited_field}")()
            new_value = getattr(self, non_inherited_field)
            if py_value != new_value:
                if non_inherited_field == "hsh":
                    # Warning only.
                    changes["hsh"] = new_value
                    # print(f"WARNING: {TypeMatchError(py_class, non_inherited_field, py_value, new_value)}")
                else:
                    print(dir(py_class))
                    print("ERR:", py_class.__name__, non_inherited_field, py_value, new_value)
                    print(getattr(py_class, "_hkMatrix4__tag_format_flags"))
                    print(py_class.get_type_name(True))
                    print(py_class.get_tag_format_flags())
                    exit()
                    raise TypeMatchError(py_class, non_inherited_field, py_value, new_value)
        # Check member info.
        if (py_member_count := len(py_class.local_members)) != (new_member_count := len(self.members)):
            raise TypeMatchError(py_class, "len(local_members)", py_member_count, new_member_count)
        for i, (py_member, new_member) in enumerate(zip(py_class.local_members, self.members)):
            if py_member.offset != new_member.offset:
                raise TypeMatchError(py_class, f"member {py_member.name}.offset", py_member.offset, new_member.offset)
            if py_member.name != new_member.name:
                raise TypeMatchError(py_class, f"member {py_member.name}.name", py_member.name, new_member.name)
            if MemberFlags.Default | py_member.extra_flags != new_member.flags:
                raise TypeMatchError(
                    py_class, f"member {py_member.name}.flags",
                    MemberFlags.Default | py_member.extra_flags, new_member.flags,
                )
            if py_member.type is None:
                raise ValueError(f"Defined Member {py_member.name} has type `None`. TypeInfo: {self}")

            # TODO: Should also check member type, but that's a little more complex with the array/enum wrappers, etc.

        return changes

    def get_class_py_def(self, defined_type_names: list[str] = (), import_undefined_names=False) -> str:
        return PyDefBuilder(self, defined_type_names, import_undefined_names).build()

    def get_parent_string(self):
        return (
            f"{self.parent_type_info.name if self.parent_type_info else None} | "
            f"{self.parent_type_py_name} | {self.parent_type_index}"
        )

    def get_pointer_string(self):
        return (
            # f"{self.pointer_type_index} | "
            f"{self.pointer_type_info.name if self.pointer_type_info else None} | "
            f"{self.pointer_type_py_name if self.pointer_type_py_name else None}"
        )

    def get_rough_py_def(self):
        """Formatted string that is a good starting point for manually defining this type."""
        parent = self.parent_type_info.name if self.parent_type_info else "hk"
        py_def = (
            f"class {self.py_name}({parent}):\n"
            f"    alignment = {self.alignment}\n"
            f"    byte_size = {self.byte_size}\n"
            f"    tag_type_flags = {self.tag_type_flags}"
        )
        if self.tag_format_flags:
            py_def += f"\n\n    __tag_format_flags = {self.tag_format_flags}"

        if self.hsh:
            py_def += f"\n    __hsh = {self.hsh}"
        if self.abstract_value:
            py_def += f"\n    __abstract_value = {self.abstract_value}"
        if self.version:
            py_def += f"\n    __version = {self.version}"

        if self.name != self.py_name:
            py_def += f"\n    __real_name = \"{self.name}\""

        if self.members:
            py_def += f"\n\n    local_members = (\n"
            for member in self.members:
                if member.type_info.name in ("hkArray",):
                    type_py_name = f"{member.type_info.name}({member.type_info.templates[0].type_info.py_name})"
                elif member.type_info.name == "hkEnum":
                    type_py_name = (
                        f"hkEnum({member.type_info.templates[0].type_info.py_name}, "
                        f"{member.type_info.templates[1].type_info.py_name})"
                    )
                elif member.type_info.name == "T*":
                    type_py_name = f"Ptr({member.type_info.templates[0].type_info.py_name})"
                else:
                    type_py_name = member.type_py_name
                py_def += (
                    f"        Member({member.offset}, \"{member.name}\", {type_py_name}, "
                    f"{member.get_tag_member_flags_repr()}),\n"
                )
            py_def += "    )"

        # TODO: templates, interfaces

        return py_def

    def get_new_type_module_and_import(self, base_names: list[str]) -> tuple[str, str]:
        """Construct best attempt at a Python definition for the given `TypeInfo`.

        `base_names` should be a list of class names defined in `hk20XX.core`.

        Returns the complete Python module string and an import line to add to `hk20XX.__init__`.
        """
        py_name = self.py_name
        py_def = self.get_class_py_def(base_names, True)

        return self._PY_DEF_HEADER + py_def, f"from .{py_name} import {py_name}"

    def __repr__(self) -> str:
        members = "["
        for m in self.members:
            members += f"\n        {m},"
        members += "\n    ]"
        return (
            f"TypeInfo(\n"
            f"    name={self.name},\n"
            f"    templates={self.templates},\n"
            f"    parent=<{self.get_parent_string()}>,\n"
            f"    tag_format_flags={self.tag_format_flags},\n"
            f"    tag_type_flags={self.tag_type_flags},\n"
            f"    pointer=<{self.get_pointer_string()}>,\n"
            f"    version={self.version},\n"
            f"    byte_size={self.byte_size},\n"
            f"    alignment={self.alignment},\n"
            f"    abstract_value={self.abstract_value},\n"
            f"    members={members},\n"
            f"    interfaces={self.interfaces},\n"
            f")"
        )
