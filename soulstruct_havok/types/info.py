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

import re
import typing as tp

from soulstruct_havok.enums import TagDataType, TagFormatFlags, MemberFlags

from .exceptions import HavokTypeError, TypeNotDefinedError, TypeMatchError

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


class TemplateInfo:
    """Simple container for an unpacked template name and value."""
    name: str
    value: None | int  # will be a type index if name starts with 't'
    type_info: None | TypeInfo
    type_py_name: None | str

    def __init__(self, name: str, value: int = -1, type_info: TypeInfo = None, type_py_name: str = None):
        self.name = name
        self.value = value

        self.type_info = type_info
        self.type_py_name = type_py_name

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


class MemberInfo:
    """Simple container for information about a specific member of a single type."""
    name: str
    flags: int
    offset: int
    type_index: tp.Optional[int]
    type_info: tp.Optional[TypeInfo]
    type_py_name: tp.Optional[str]

    # Attributes used temporaneously by Python auto-generator.
    member_py_name: None | str
    type_hint: None | str
    required_types: list[str]

    def __init__(
        self,
        name: str,
        flags: int,
        offset: int,
        type_index: int = None,
        type_info: TypeInfo = None,
        type_py_name: str = None,
    ):
        self.name = name
        self.flags = flags
        self.offset = offset
        self.type_index = type_index

        # Deindexified attributes.
        self.type_info = type_info
        self.type_py_name = type_py_name

        self.member_py_name = None
        self.type_hint = None
        self.required_types = []

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
            f"MemberInfo(\"{self.name}\", {self.type_py_name} <{self.type_index}>, "
            f"flags={self.flags}, offset={self.offset})"
        )


class InterfaceInfo:
    """Simple container for information about an interface of a single type."""
    flags: int
    type_index: tp.Optional[int]
    type_info: tp.Optional[TypeInfo]
    type_py_name: tp.Optional[str]

    def __init__(self, flags: int, type_index: int = None, type_info: TypeInfo = None, type_py_name: str = None):
        self.flags = flags
        self.type_index = type_index

        self.type_info = type_info
        self.type_py_name = type_py_name

    def indexify(self, type_py_names: list[str]):
        self.type_index = type_py_names.index(self.type_py_name)

    def __repr__(self):
        return f"InterfaceInfo({self.flags}, <{self.type_py_name}>)"


class TypeInfo:
    """Holds information about a type, temporarily. Designed to correspond 1-for-1 with types unpacked from tagfiles,
    including all generic types like hkArray, T*, T[N], etc.

    Initialized first with just name and template (from "TNAM" section), then remaining info later. Only used to compare
    against known types, and to help add to those known types if new.
    """

    GENERIC_TYPE_NAMES = [
        "hkArray", "hkEnum", "hkRefPtr", "hkRefVariant", "hkViewPtr", "T*", "T[N]", "hkRelArray", "hkFlags",
        "hkFreeListArray", "hkFreeListArrayElement",
    ]

    templates: list[TemplateInfo]
    parent_type_index: None | int
    tag_format_flags: None | int
    tag_type_flags: None | int
    pointer_type_index: None | int
    version: None | int
    byte_size: None | int
    alignment: None | int
    abstract_value: None | int
    members: list[MemberInfo]
    interfaces: list[InterfaceInfo]
    hsh: None | int

    parent_type_info: None | TypeInfo
    parent_type_py_name: None | str
    pointer_type_info: None | TypeInfo
    pointer_type_py_name: None | str

    py_class: tp.Optional[tp.Type[hk]]

    _PY_DEF_HEADER = (
        "from __future__ import annotations\n\n"
        "from soulstruct_havok.types.core import *\n"
        "from soulstruct_havok.enums import *\n"
        "from .core import *\n\n\n"
    )

    def __init__(self, name: str):
        self.name = name
        self.templates = []
        self.parent_type_index = None
        self.tag_format_flags = None
        self.tag_type_flags = None
        self.pointer_type_index = None
        self.version = None
        self.byte_size = None
        self.alignment = None
        self.abstract_value = None
        self.members = []
        self.interfaces = []
        self.hsh = None

        self.parent_type_info = None
        self.parent_type_py_name = None
        self.pointer_type_info = None
        self.pointer_type_py_name = None

        self.py_class = None

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

    def get_parent_value(self, field: str):
        """Iterate up parent types until a non-zero value for `field` is found."""
        child_value = getattr(self, field)
        if child_value is not None:
            return child_value
        if self.parent_type_info is None:
            raise ValueError(f"No parent to check for `TypeInfo` {self.name} to retrieve \"{field}\".")
        return self.parent_type_info.get_parent_value(field)

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
        for field in ("tag_type_flags", "byte_size", "alignment"):
            py_value = getattr(py_class, field)
            new_value = self.get_parent_value(field)
            if py_value != new_value:
                raise TypeMatchError(py_class, field, py_value, new_value, binary=field == "tag_type_flags")
        for non_inherited_field in ("tag_format_flags", "hsh", "abstract_value", "version"):
            py_value = getattr(py_class, f"get_{non_inherited_field}")()
            new_value = getattr(self, non_inherited_field)
            if py_value != new_value:
                if non_inherited_field == "hsh":
                    # Warning only.
                    changes["hsh"] = new_value
                    # print(f"WARNING: {TypeMatchError(py_class, non_inherited_field, py_value, new_value)}")
                else:
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
            f"    members={self.members},\n"
            f"    interfaces={self.interfaces},\n"
            f")"
        )


class PyDefBuilder:

    MAX_LINE_LENGTH = 121

    info: TypeInfo
    defined_type_names: None | list[str]
    import_lines: None | list[str]

    def __init__(self, type_info: TypeInfo, defined_type_names: list[str] = (), import_undefined_names=False):
        self.info = type_info
        self.defined_type_names = defined_type_names + [type_info.name]  # may reference self
        self.import_lines = [] if import_undefined_names else None

    @property
    def name(self):
        return self.info.name

    @property
    def py_name(self) -> str:
        return self.info.py_name

    @property
    def tag_type_flags(self) -> int:
        return self.info.tag_type_flags

    @property
    def tag_data_type(self) -> TagDataType:
        return self.info.tag_data_type

    def check_defined(self, py_name: str, source_name: str, description: str):
        if py_name not in self.defined_type_names:
            if self.import_lines is not None:
                print(f"ADDING IMPORT: {py_name}")
                if py_name not in self.import_lines:
                    self.import_lines.append(py_name)
            else:
                if source_name:
                    raise TypeNotDefinedError(f"Undefined {description} type for `{source_name}`: {py_name}")
                raise TypeNotDefinedError(f"Undefined required {description} type: {py_name}")

    def build_rel_array_type(self, rel_array_type: TypeInfo) -> tuple[str, str]:
        array_data_type = rel_array_type.pointer_type_info
        py_name, type_hint = self.build_type_name(array_data_type)
        return f"hkRelArray({py_name})", f"list[{type_hint}]"

    def build_array_type(self, array_type: TypeInfo, allow_undefined=False) -> tuple[str, str]:
        array_data_type = array_type.pointer_type_info

        # TODO: hcl classes can have arrays of arrays (e.g.,
        #  hclStateTransition[simClothTransitionConstraints]). Handle this.
        #  Shouldn't be ridiculously hard...

        if array_data_type == self.info:
            # Array of type being defined. Must used `DefType` deferred wrapper.
            py_name, type_hint = self.build_array_type(array_data_type)
            if array_type.hsh is not None:
                return f"hkArray(DefType(\"{py_name}\", lambda: {py_name}), hsh={array_type.hsh})", f"list[{type_hint}]"
            return f"hkArray(DefType(\"{py_name}\", lambda: {py_name}))", f"list[{type_hint}]"

        # Note that arrays CAN (rarely) contain other arrays, e.g. `hclStateTransition.simClothTransitionConstraints`.
        py_name, type_hint = self.build_type_name(array_data_type, allow_undefined=allow_undefined)

        if array_type.hsh is not None:
            return f"hkArray({py_name}, hsh={array_type.hsh})", f"list[{type_hint}]"
        return f"hkArray({py_name})", f"list[{type_hint}]"

    def build_ref_variant_type(self, ref_variant_type: TypeInfo) -> tuple[str, str]:
        data_type_info = ref_variant_type.get_member_info("ptr").type_info.pointer_type_info
        if data_type_info.py_name != "hkReferencedObject":
            raise ValueError(
                f"`hkRefVariant` has a data type other than `hkReferencedObject`: {data_type_info.py_name}"
            )
        self.check_defined(data_type_info.py_name, "hkRefVariant", "data")
        py_name, type_hint = self.build_type_name(data_type_info)
        if ref_variant_type.hsh is not None:
            return f"hkRefVariant({py_name}, hsh={ref_variant_type.hsh})", type_hint
        return f"hkRefVariant({py_name})", type_hint

    def build_ref_ptr_type(self, ref_ptr_type: TypeInfo) -> tuple[str, str]:
        """Returns data type name and pointer-free type hint name."""
        data_type_info = ref_ptr_type.get_member_info("ptr").type_info.pointer_type_info
        py_name, type_hint = self.build_type_name(data_type_info)
        if data_type_info == self.info:
            # Pointer to type being defined. Must used `DefType` deferred wrapper.
            if ref_ptr_type.hsh is not None:
                return f"hkRefPtr(DefType(\"{py_name}\", lambda: {py_name}), hsh={ref_ptr_type.hsh})", type_hint
            return f"hkRefPtr(DefType(\"{py_name}\", lambda: {py_name}))", type_hint
        self.check_defined(data_type_info.py_name, "hkRefPtr", "data")
        if ref_ptr_type.hsh is not None:
            return f"hkRefPtr({py_name}, hsh={ref_ptr_type.hsh})", type_hint
        return f"hkRefPtr({py_name})", type_hint

    def build_ptr_type(self, ptr_type: TypeInfo) -> tuple[str, str]:
        data_type_info = ptr_type.pointer_type_info
        py_name, type_hint = self.build_type_name(data_type_info)
        if data_type_info == self.info:
            # Pointer to type being defined. Must used `DefType` deferred wrapper.
            if ptr_type.hsh is not None:
                return f"Ptr(DefType(\"{py_name}\", lambda: {py_name}), hsh={ptr_type.hsh})", type_hint
            return f"Ptr(DefType(\"{py_name}\", lambda: {py_name}))", type_hint
        self.check_defined(data_type_info.py_name, "Ptr", "data")
        if ptr_type.hsh is not None:
            return f"Ptr({py_name}, hsh={ptr_type.hsh})", type_hint
        return f"Ptr({py_name})", type_hint

    def build_view_ptr_type(self, view_ptr_type: TypeInfo) -> tuple[str, str]:
        data_type_info = view_ptr_type.get_member_info("ptr").type_info.pointer_type_info
        hsh = view_ptr_type.get_member_info("ptr").type_info.hsh
        # `hkViewPtr` data types are ALWAYS permitted to be undefined.
        py_name, type_hint = self.build_type_name(data_type_info, allow_undefined=True)
        if data_type_info == self.info:
            if hsh is not None:
                return f"hkViewPtr(DefType(\"{py_name}\", lambda: {py_name}), hsh={hsh})", type_hint
            return f"hkViewPtr(DefType(\"{py_name}\", lambda: {py_name}))", type_hint
        # No need to check that view type has already been defined, as it's deferred anyway
        if hsh is not None:
            return f"hkViewPtr(\"{py_name}\", hsh={hsh})", type_hint
        return f"hkViewPtr(\"{py_name}\")", type_hint

    def build_struct_type(self, struct_type: TypeInfo) -> tuple[str, str]:
        """Generic `T[N]` struct, NOT a struct "subclass" like `hkVector4`."""
        data_type_info = struct_type.pointer_type_info
        struct_length = struct_type.templates[1].value  # "vN" template
        if data_type_info.name == "T*":
            # Struct of pointers.
            py_name, type_hint = self.build_ptr_type(data_type_info)
        else:
            # Struct of primitives.
            py_name = type_hint = data_type_info.py_name
            self.check_defined(py_name, "hkStruct", "data")
        return f"hkGenericStruct({py_name}, {struct_length})", f"tuple[{type_hint}]"

    def build_enum_type(self, enum_type: TypeInfo) -> tuple[str, str]:
        t_enum_type = enum_type.templates[0].type_info  # "tENUM" template
        t_storage_type = enum_type.templates[1].type_info  # "tSTORAGE" template
        self.check_defined(t_enum_type.py_name, "hkEnum", "enum")
        self.check_defined(t_storage_type.py_name, "hkEnum", "storage")
        return f"hkEnum({t_enum_type.py_name}, {t_storage_type.py_name})", t_enum_type.py_name

    def build_free_list_array_element_type(self, element_type: TypeInfo) -> tuple[str, str]:
        element_parent_type = element_type.parent_type_info
        self.check_defined(element_parent_type.py_name, "hkFreeListArrayElement", "parent")
        return f"hkFreeListArrayElement({element_parent_type})", element_parent_type.py_name

    def build_free_list_array_type(self, free_list_array_type: TypeInfo) -> tuple[str, str]:
        elements_data_type = free_list_array_type.members[0].type_info.pointer_type_info
        hsh = elements_data_type.hsh
        first_free_type = free_list_array_type.members[1].type_info
        if elements_data_type.py_name != "hkFreeListArrayElement":
            raise HavokTypeError(
                f"Expected 'elements' data type for `hkFreeListArray` to be `hkFreeListArrayElement`, "
                f"not: {elements_data_type.py_name}"
            )
        elements_data_parent_type = elements_data_type.parent_type_info
        self.check_defined(elements_data_parent_type.py_name, "hkFreeListArray", "`elements` parent")
        self.check_defined(first_free_type.py_name, "hkFreeListArray", "`firstFree`")
        if hsh is not None:
            return (
                f"hkFreeListArray({elements_data_parent_type.py_name}, {first_free_type.py_name}, hsh={hsh})",
                f"list[{elements_data_parent_type.py_name}]",
            )
        return (
            f"hkFreeListArray({elements_data_parent_type.py_name}, {first_free_type.py_name})",
            f"list[{elements_data_parent_type.py_name}]",
        )

    def build_flags_type(self, flags_type: TypeInfo) -> tuple[str, str]:
        # storage_type = flags_type.members[0].type_info
        storage_type = flags_type.templates[1].type_info
        self.check_defined(storage_type.py_name, "hkFlags", "storage")
        return f"hkFlags({storage_type.py_name})", storage_type.py_name

    def build_type_name(self, type_info: TypeInfo, allow_undefined=False) -> tuple[str, str]:
        """Determine Python type for member definition.

        Returns both the true type string (for packing/unpacking), e.g. `hkArray(Ptr(hkaSkeleton))`, and the type hint
        for the Python object that will actually represent this member, e.g. `list[hkaSkeleton]`.
        """

        if type_info.name == "hkFreeListArrayElement":
            return self.build_free_list_array_element_type(type_info)
        elif type_info.name == "hkFreeListArray":
            return self.build_free_list_array_type(type_info)
        elif type_info.name == "hkFlags":
            return self.build_flags_type(type_info)
        elif type_info.name == "hkArray":
            return self.build_array_type(type_info)
        elif type_info.name == "hkRelArray":
            return self.build_rel_array_type(type_info)
        elif type_info.name == "T[N]":
            return self.build_struct_type(type_info)
        elif type_info.name == "hkEnum":
            return self.build_enum_type(type_info)
        elif (
            (ptr_type_info := type_info.pointer_type_info) is not None
            and ptr_type_info.name != "float"  # ignore float "pointers" in struct types like `hkVector4f`
        ):
            # hkRefVariant, hkRefPtr, or Ptr (T*)
            if type_info.name == "hkRefVariant":
                return self.build_ref_variant_type(type_info)
            elif type_info.name == "hkRefPtr":
                return self.build_ref_ptr_type(type_info)
            elif type_info.name == "hkViewPtr":
                return self.build_view_ptr_type(type_info)

            # TODO: New pointer types that need support.
            #  Rather than trying to anticipate and hard-code all of these, just have them inherit from `hkBasePointer`
            #  when generated, and use that information on unpacking/packing to treat them properly. (Any subclass of
            #  `hkBasePointer` will have a `tTYPE` template that can be checked.)
            elif type_info.name == "hkReflect::QualifiedType":
                self.check_defined("hkReflectQualifiedType", "", "pointer")
                return "hkReflectQualifiedType", "hkReflectQualifiedType"
            elif type_info.name == "hkPropertyBag":
                self.check_defined("hkPropertyBag", "", "pointer")
                return "hkPropertyBag", "hkPropertyBag"

            elif type_info.name == "T*":
                return self.build_ptr_type(type_info)
            else:
                print(type_info)
                print(type_info.members[0].type_info.pointer_type_info)
                raise HavokTypeError(
                    f"Unrecognized pointer type name: {type_info.name}. "
                    f"Only `hkRefVariant`, `hkRefPtr`, `hkViewPtr`, and `T*` are known."
                )
        else:
            # Primitive or direct type.
            if not allow_undefined:
                self.check_defined(type_info.py_name, self.name, "primitive/class member")
            if type_hint := type_info.get_parent_value("tag_data_type").get_primitive_type_hint():
                return type_info.py_name, type_hint
            return type_info.py_name, type_info.py_name

    def build(self) -> str:
        """Generate Python `class` definition string for given `type_info` to be added to a module.

        Requires a full list of dereferenced `TypeInfo`s (i.e., with `TypeInfo`s set for parents, pointers, members,
        etc.) so that those classes can be referenced properly here, under the presumption that those Python classes
        will be defined BEFORE this class in the module. It checks `defined_types`, a list of Python class names already
        added to the module, to ensure that this is correct.
        """
        print(f"Building def for {self.py_name}")
        append_to_parent_members = False

        if self.tag_data_type == TagDataType.Struct:
            struct_length = (self.tag_type_flags & 0b11111111_00000000) >> 8
            parent_name = f"hkStruct({self.info.pointer_type_info.py_name}, {struct_length})"
        else:
            if self.info.parent_type_info is not None:
                parent_name = self.info.parent_type_info.py_name
                append_to_parent_members = True
                self.check_defined(parent_name, self.name, "parent")
            elif self.info.pointer_type_info is not None and self.info.name not in {"T*", "hkRefPtr", "hkRefVariant"}:
                parent_name = "hkBasePointer"
            else:
                parent_name = "hk"

        py_string = f"class {self.py_name}({parent_name}):\n"

        if self.tag_type_flags is None and self.name != "void":
            # Bare alias wrapper. Just define hash and empty members.
            assert (self.info.alignment is None)
            assert (self.info.byte_size is None)
            py_string += "    \"\"\"Havok alias.\"\"\"\n"
            py_string += f"    __tag_format_flags = {self.info.tag_format_flags}\n"
            if self.info.hsh:
                py_string += f"    __hsh = {self.info.hsh}\n"
            if self.info.version:
                py_string += f"    __version = {self.info.version}\n"
            if self.py_name != self.name:
                py_string += f"    __real_name = \"{self.name}\"\n"
            py_string += "    local_members = ()\n"
            return py_string

        py_string += f"    alignment = {self.info.alignment}\n"
        py_string += f"    byte_size = {self.info.byte_size}\n"
        py_string += f"    tag_type_flags = {self.info.get_tag_type_flags_repr()}\n"

        newline_done = False
        for not_inherited_field in ("tag_format_flags", "hsh", "abstract_value", "version"):
            value = getattr(self.info, not_inherited_field)
            if value is not None:
                if not newline_done:
                    py_string += "\n"  # new line between inherited and non-inherited fields
                    newline_done = True
                py_string += f"    __{not_inherited_field} = {value}\n"

        if self.py_name != self.name:
            py_string += f"    __real_name = \"{self.name}\"\n"

        if parent_name == "hkBasePointer":
            py_string += f"    _data_type = {self.info.pointer_type_info.py_name}"

        if self.info.members:
            member_attr_hints = {}

            py_string += f"\n    local_members = (\n"  # new line before members
            for member in self.info.members:
                # noinspection PyUnresolvedReferences
                if member.type_info is None:
                    # TODO: Trying to use packfile information only.
                    py_name = member.member_py_name
                    type_hint = member.type_hint
                    if self.defined_type_names and any(
                        name not in self.defined_type_names for name in member.required_types
                    ):
                        raise TypeNotDefinedError(f"Packfile type(s) not defined: {member.required_types}")
                    # raise ValueError(f"Member '{member.name}' of `{self.py_name}` has no `TypeInfo` assigned.")
                else:
                    print(f"  Member {member.name} (type {member.type_info.name})")
                    py_name, type_hint = self.build_type_name(member.type_info)
                    print(f"    --> {py_name} | {type_hint}")
                member_string = f"        Member({member.offset}, \"{member.name}\", {py_name}"
                if member.flags != MemberFlags.Default:
                    member_string += f", {member.get_tag_member_flags_repr()}),\n"
                else:
                    member_string += "),\n"
                if len(member_string) > self.MAX_LINE_LENGTH - 8:  # account for indent
                    # Reformat with line breaks.
                    member_string = (
                        f"        Member(\n"
                        f"            {member.offset},\n"
                        f"            \"{member.name}\",\n"
                        f"            {py_name},\n"
                    )
                    if member.flags != MemberFlags.Default:
                        member_string += f"            {member.get_tag_member_flags_repr()},\n"
                    member_string += f"        ),\n"
                py_string += member_string
                member_attr_hints[member.name] = type_hint
            py_string += f"    )\n"

            if append_to_parent_members:
                py_string += f"    members = {parent_name}.members + local_members\n"
            else:
                py_string += f"    members = local_members\n"
            if member_attr_hints:
                first_newline_done = False
                for member_name, member_type_hint in member_attr_hints.items():
                    if re.match(r"^[A-z_]", member_name):
                        if not first_newline_done:
                            first_newline_done = True
                            py_string += "\n"
                        py_string += f"    {member_name}: {member_type_hint}\n"
        else:
            # No local members. (`members` can be directly inherited from parent.)
            py_string += f"    local_members = ()\n"

        if self.info.templates:
            py_string += "\n"
            py_string += f"    __templates = (\n"
            for template_info in self.info.templates:
                if template_info.is_type:
                    template_type_py_name, _ = self.build_type_name(template_info.type_info)
                    py_string += f"        TemplateType(\"{template_info.name}\", type={template_type_py_name}),\n"
                elif template_info.is_value:
                    py_string += f"        TemplateValue(\"{template_info.name}\", value={template_info.value}),\n"
                else:
                    raise ValueError(f"Template name does not start with 't' or 'v': {template_info.name}")
            py_string += f"    )\n"

        if self.info.interfaces:
            py_string += "\n"
            py_string += f"    __interfaces = (\n"
            for interface_info in self.info.interfaces:
                interface_type_py_name = interface_info.type_info.py_name
                self.check_defined(interface_type_py_name, self.name, "interface")
                py_string += f"        Interface({interface_type_py_name}, flags={interface_info.flags}),\n"
            py_string += f"    )\n"

        if self.import_lines:
            py_string = "\n".join(f"from .{t} import {t}" for t in self.import_lines) + f"\n\n\n{py_string}"

        return py_string
