"""Classes for representing direct information about a Havok type unpacked from, or to be packed to, a file."""
from __future__ import annotations

__all__ = [
    "TemplateInfo",
    "MemberInfo",
    "InterfaceInfo",
    "TypeInfo",
    "TypeNotDefinedError",
    "TypeMatchError",
    "get_py_name",
]

import re
import typing as tp

from soulstruct_havok.enums import TagDataType

if tp.TYPE_CHECKING:
    from .core import hk


class TypeNotDefinedError(Exception):
    """Raised when an undefined parent or member is encountered."""


class TypeMatchError(Exception):
    """Raised when a Python class's information clashes with a new `TypeInfo`."""
    def __init__(self, py_class: tp.Type[hk], field_name: str, py_value, new_value):
        super().__init__(
            f"Python type `{py_class.__name__}` has {field_name} = {py_value}, but this `TypeInfo` has "
            f"{field_name} = {new_value}."
        )


def get_py_name(real_name: str) -> str:
    py_name = real_name.replace("::", "").replace(" ", "_").replace("*", "")
    if not py_name.startswith("hk"):
        py_name = "_" + py_name  # for 'int', 'const_char', etc.
    return py_name


class TemplateInfo:
    """Simple container for an unpacked template name and value."""
    name: str
    value: tp.Optional[int]  # will be a type index if name starts with 't'
    type_info: tp.Optional[TypeInfo]
    type_py_name: tp.Optional[str]

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
            return f"TemplateInfo(\"{self.name}\", <{self.type_info.name}>)"
        return f"TemplateInfo(\"{self.name}\", {self.value})"


class MemberInfo:
    """Simple container for information about a specific member of a single type."""
    name: str
    flags: int
    offset: int
    type_index: tp.Optional[int]
    type_info: tp.Optional[TypeInfo]
    type_py_name: tp.Optional[str]

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

        self.type_info = type_info
        self.type_py_name = type_py_name

    def indexify(self, type_py_names: list[str]):
        try:
            self.type_index = type_py_names.index(self.type_py_name)
        except ValueError:
            raise ValueError(f"Could not find {self.type_py_name} in types (member \"{self.name}\")")

    def __repr__(self):
        return f"MemberInfo(\"{self.name}\", <{self.type_py_name}>, flags={self.flags}, offset={self.offset})"


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

    GENERIC_TYPE_NAMES = ["hkArray", "hkEnum", "hkRefPtr", "hkRefVariant", "hkViewPtr", "T*", "T[N]"]

    def __init__(self, name: str):
        self.name = name
        self.templates = []  # type: list[TemplateInfo]
        self.parent_type_index = None  # type: tp.Optional[int]
        self.tag_format_flags = None  # type: tp.Optional[int]
        self.tag_type_flags = None  # type: tp.Optional[int]
        self.pointer_type_index = None  # type: tp.Optional[int]
        self.version = None  # type: tp.Optional[int]
        self.byte_size = None  # type: tp.Optional[int]
        self.alignment = None  # type: tp.Optional[int]
        self.abstract_value = None  # type: tp.Optional[int]
        self.members = []  # type: list[MemberInfo]
        self.interfaces = []  # type: list[InterfaceInfo]
        self.hsh = None  # type: tp.Optional[int]

        self.parent_type_info = None  # type: tp.Optional[TypeInfo]
        self.parent_type_py_name = None  # type: tp.Optional[str]
        self.pointer_type_info = None  # type: tp.Optional[TypeInfo]
        self.pointer_type_py_name = None  # type: tp.Optional[str]

        self.py_class = None  # type: tp.Optional[tp.Type[hk]]

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

    @property
    def py_name(self) -> str:
        return get_py_name(self.name)

    def check_py_class_match(self, py_class: tp.Type[hk]):
        """Check `TypeInfo` attributes (typically from a file) against attributes of pre-defined Python class.

        Raises a `TypeMatchError` if a clash occurs, and does nothing otherwise.
        """

        if self.parent_type_py_name is not None:
            py_parent_name = py_class.__bases__[-1].__name__
            if self.parent_type_py_name != py_parent_name:
                raise TypeMatchError(py_class, "parent", py_parent_name, self.parent_type_py_name)
        for field in ("tag_type_flags", "byte_size", "alignment"):
            py_value = getattr(py_class, field)
            new_value = self.get_parent_value(field)
            if py_value != new_value:
                raise TypeMatchError(py_class, field, py_value, new_value)
        for non_inherited_field in ("tag_format_flags", "hsh", "abstract_value", "version"):
            py_value = getattr(py_class, f"get_{non_inherited_field}")()
            new_value = getattr(self, non_inherited_field)
            if py_value != new_value:
                if non_inherited_field == "hsh":
                    # Warning only.
                    print(f"WARNING: {TypeMatchError(py_class, non_inherited_field, py_value, new_value)}")
                else:
                    raise TypeMatchError(py_class, non_inherited_field, py_value, new_value)
        # Check member info.
        if (py_member_count := len(py_class.local_members)) != (new_member_count := len(self.members)):
            raise TypeMatchError(py_class, "len(local_members)", py_member_count, new_member_count)
        for i, (py_member, new_member) in enumerate(zip(py_class.local_members, self.members)):
            for member_field in ("name", "flags", "offset"):
                if (py_value := getattr(py_member, member_field)) != (new_value := getattr(new_member, member_field)):
                    raise TypeMatchError(py_class, f"member {py_member.name}.{member_field}", py_value, new_value)

            # TODO: Should also check member type, but that's a little more complex with the array/enum wrappers, etc.

    def get_py_class_def(self, defined_types: list[str]) -> str:
        """Generate Python `class` definition string for this `TypeInfo` to be added to a module.

        Requires a full list of dereferenced `TypeInfo`s (i.e., with `TypeInfo`s set for parents, pointers, members,
        etc.) so that those classes can be referenced properly here, under the presumption that those Python classes
        will be defined BEFORE this class in the module. It checks `defined_types`, a list of Python class names already
        added to the module, to ensure that this is correct.
        """

        member = None

        def get_ref_ptr_name(hk_ref_ptr_type: TypeInfo) -> tuple[str, str]:
            """Returns data type name and pointer-free type hint name."""
            data_type_info = hk_ref_ptr_type.get_member_info("ptr").type_info.pointer_type_info
            data_type_py_name = data_type_info.py_name
            hsh = hk_ref_ptr_type.hsh
            if data_type_info == self:
                return f"hkRefPtr(DefType(\"{data_type_py_name}\", lambda: {data_type_py_name}), hsh={hsh})", data_type_py_name
            if data_type_py_name not in defined_types:
                raise TypeNotDefinedError(
                    f"Undefined member type (hkRefPtr) for `{self.name}[{member.name}]`: "
                    f"`{data_type_py_name}`"
                )
            return f"hkRefPtr({data_type_py_name}, hsh={hsh})", data_type_py_name

        def get_ref_variant_name(hk_ref_variant_type: TypeInfo) -> tuple[str, str]:
            """Returns data type name and pointer-free type hint name."""
            data_type_info = hk_ref_variant_type.get_member_info("ptr").type_info.pointer_type_info
            data_type_py_name = data_type_info.py_name
            if data_type_py_name != "hkReferencedObject":
                raise ValueError(f"`hkRefVariant` has a data type other than `hkReferencedObject`: {data_type_py_name}")
            hsh = hk_ref_variant_type.hsh
            if data_type_py_name not in defined_types:
                raise TypeNotDefinedError(
                    f"Undefined member type (hkRefPtr) for `{self.name}[{member.name}]`: "
                    f"`{data_type_py_name}`"
                )
            return f"hkRefVariant({data_type_py_name}, hsh={hsh})", data_type_py_name

        def get_ptr_name(ptr_type: TypeInfo) -> tuple[str, str]:
            data_type_info = ptr_type.pointer_type_info
            data_type_py_name = data_type_info.py_name
            hsh = ptr_type.hsh
            if data_type_info == self:
                return f"Ptr(DefType(\"{data_type_py_name}\", lambda: {data_type_py_name}), hsh={hsh})", data_type_py_name
            if data_type_py_name not in defined_types:
                raise TypeNotDefinedError(
                    f"Undefined member type (pointer) for `{self.name}[{member.name}]`: "
                    f"`{data_type_py_name}`"
                )
            return f"Ptr({data_type_py_name}, hsh={hsh})", data_type_py_name

        def get_view_ptr_name(hk_view_ptr_type: TypeInfo) -> tuple[str, str]:
            data_type_info = hk_view_ptr_type.get_member_info("ptr").type_info.pointer_type_info
            data_type_py_name = data_type_info.py_name
            hsh = hk_view_ptr_type.get_member_info("ptr").type_info.hsh
            if data_type_info == self:
                return (
                    f"hkViewPtr(DefType(\"{data_type_py_name}\", lambda: {data_type_py_name}), hsh={hsh})",
                    data_type_py_name
                )
            # No need to check that view type has already been defined, as it's deferred anyway
            return f"hkViewPtr(\"{data_type_py_name}\", hsh={hsh})", data_type_py_name

        py_name = self.py_name
        tag_data_type = self.tag_data_type
        append_to_parent_members = False

        if tag_data_type == TagDataType.Struct:
            if TagDataType.IsVector4.has_flag(self.tag_type_flags):
                struct_type_name, struct_length = "_float", 4
            elif TagDataType.IsTransform.has_flag(self.tag_type_flags):
                struct_type_name, struct_length = "_float", 16
            elif TagDataType.IsMatrix3Impl.has_flag(self.tag_type_flags):
                struct_type_name, struct_length = "_float", 12
            else:
                raise ValueError(f"Invalid `hkStruct` data subtype. Flags: {self.tag_type_flags:b}")
            parent_name = f"hkStruct({struct_type_name}, {struct_length})"
        else:
            if self.parent_type_info is None:
                parent_name = "hk"
            else:
                parent_name = self.parent_type_info.py_name
                append_to_parent_members = True
            if parent_name not in defined_types:
                raise TypeNotDefinedError(f"Undefined parent for `{self.name}`: `{parent_name}`")

        py_string = f"class {py_name}({parent_name}):\n"

        if self.tag_type_flags is None and self.name != "void":
            # Bare alias wrapper. Just define hash and empty members.
            assert (self.alignment is None)
            assert (self.byte_size is None)
            assert (self.tag_format_flags == 0)
            py_string += "    \"\"\"Havok alias.\"\"\"\n"
            if self.hsh:
                py_string += f"    __hsh = {self.hsh}\n"
            py_string += "    __tag_format_flags = 0\n"
            py_string += "    local_members = ()\n"
            return py_string

        for field in ("alignment", "byte_size", "tag_type_flags"):
            py_string += f"    {field} = {getattr(self, field)}\n"

        newline_done = False
        for not_inherited_field in ("tag_format_flags", "hsh", "abstract_value", "version"):
            value = getattr(self, not_inherited_field)
            if value is not None:
                if not newline_done:
                    py_string += "\n"  # new line between inherited and non-inherited fields
                    newline_done = True
                py_string += f"    __{not_inherited_field} = {value}\n"

        if py_name != self.name:
            py_string += f"    __real_name = \"{self.name}\"\n"

        if self.members:
            py_string += "\n"  # new line before members
            member_attr_hints = {}
            py_string += f"    local_members = (\n"
            for member in self.members:
                print(member.name, member.type_info)
                member_type_info = member.type_info

                # TODO: Determine how 'NewStruct' will be detected from 2014 packfiles.
                if py_name in {"hknpConvexShape", "hknpConvexPolytopeShape"}:
                    # All members are `NewStruct` but are incorrectly stored as `hkArray` in the XML.
                    struct_type = member_type_info.pointer_type_info
                    member_type_py_name = f"NewStruct({struct_type.py_name})"
                    member_attr_hints[member.name] = f"tuple[{struct_type.py_name}]"
                elif member_type_info.name == "hkArray":
                    array_type_info = member_type_info.pointer_type_info
                    if array_type_info == self:  # arrays do not contain other arrays, so this shouldn't ever happen
                        array_type_py_name = f"DefType(\"{py_name}\", lambda: {py_name})"
                        type_hint_py_name = py_name
                    elif array_type_info.name == "hkRefVariant":
                        array_type_py_name, type_hint_py_name = get_ref_variant_name(array_type_info)
                    elif array_type_info.name == "hkRefPtr":
                        array_type_py_name, type_hint_py_name = get_ref_ptr_name(array_type_info)
                    elif array_type_info.name == "T*":
                        array_type_py_name, type_hint_py_name = get_ptr_name(array_type_info)
                    elif array_type_info.name == "hkViewPtr":
                        array_type_py_name, type_hint_py_name = get_view_ptr_name(array_type_info)
                    else:
                        # Array of primitives.
                        array_type_py_name = array_type_info.py_name
                        type_hint_py_name = array_type_py_name
                        if array_type_py_name not in defined_types:
                            raise TypeNotDefinedError(
                                f"Undefined member array type for `{self.name}[{member.name}]`: "
                                f"`{array_type_py_name}`"
                            )
                    hsh = member_type_info.hsh
                    member_type_py_name = f"hkArray({array_type_py_name}, hsh={hsh})"
                    member_attr_hints[member.name] = f"list[{type_hint_py_name}]"
                elif member_type_info.name == "T[N]":
                    struct_type_info = member_type_info.pointer_type_info
                    struct_length = member_type_info.templates[1].value  # "vN" template
                    if struct_type_info.name == "T*":
                        struct_type_py_name, type_hint_py_name = get_ptr_name(struct_type_info)
                    else:  # no `hkRefPtr` or `hkViewPtr` for Structs
                        struct_type_py_name = type_hint_py_name = struct_type_info.py_name
                        if struct_type_py_name not in defined_types:
                            raise TypeNotDefinedError(
                                f"Undefined member struct type for `{self.name}[{member.name}]`: "
                                f"`{struct_type_py_name}`"
                            )
                    struct_tag_subtype = TagDataType(member_type_info.tag_type_flags >> 8 << 8)
                    member_type_py_name = (
                        f"hkStruct({struct_type_py_name}, {struct_length}, TagDataType.{struct_tag_subtype.name})"
                    )
                    member_attr_hints[member.name] = f"tuple[{type_hint_py_name}, ...]"
                elif member_type_info.name == "hkEnum":
                    enum_type = member_type_info.templates[0].type_info  # "tENUM" template
                    storage_type = member_type_info.templates[1].type_info  # "tSTORAGE" template
                    enum_type_py_name = enum_type.py_name
                    storage_type_py_name = storage_type.py_name
                    if enum_type_py_name not in defined_types:
                        raise TypeNotDefinedError(
                            f"Undefined hkEnum data type for `{self.name}[{member.name}]`: "
                            f"`{enum_type_py_name}`"
                        )
                    if storage_type_py_name not in defined_types:
                        raise TypeNotDefinedError(
                            f"Undefined hkEnum storage type for `{self.name}[{member.name}]`: "
                            f"`{storage_type_py_name}`"
                        )
                    member_type_py_name = f"hkEnum({enum_type_py_name}, {storage_type_py_name})"
                    member_attr_hints[member.name] = enum_type_py_name
                elif (
                    (ptr_type_info := member_type_info.pointer_type_info) is not None
                    and ptr_type_info.name != "float"  # ignore float "pointers" in struct types like `hkVector4f`
                ):
                    if member_type_info.name == "hkRefVariant":
                        member_type_py_name, type_hint_py_name = get_ref_variant_name(member_type_info)
                    elif member_type_info.name == "hkRefPtr":
                        member_type_py_name, type_hint_py_name = get_ref_ptr_name(member_type_info)
                    else:
                        # Standard 'T*' pointer.
                        member_type_py_name, type_hint_py_name = get_ptr_name(member_type_info)
                    member_attr_hints[member.name] = type_hint_py_name
                else:
                    member_type_py_name = member_type_info.py_name
                    if member_type_py_name not in defined_types:
                        raise TypeNotDefinedError(
                            f"Undefined member type for `{self.name}[{member.name}]`: `{member_type_py_name}`"
                        )
                    member_attr_hints[member.name] = member_type_py_name
                py_string += (
                    f"        Member(\"{member.name}\", {member_type_py_name}, "
                    f"offset={member.offset}, flags={member.flags}),\n"
                )
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

        if self.templates:
            py_string += "\n"
            py_string += f"    __templates = (\n"
            for template_info in self.templates:
                if template_info.is_type:
                    template_type_py_name = template_info.type_info.py_name
                    py_string += f"        TemplateType(\"{template_info.name}\", type={template_type_py_name}),\n"
                elif template_info.is_value:
                    py_string += f"        TemplateValue(\"{template_info.name}\", value={template_info.value}),\n"
                else:
                    raise ValueError(f"Template name does not start with 't' or 'v': {template_info.name}")
            py_string += f"    )\n"

        if self.interfaces:
            py_string += "\n"
            py_string += f"    __interfaces = (\n"
            for interface_info in self.interfaces:
                interface_type_py_name = interface_info.type_info.py_name
                py_string += f"        Interface({interface_type_py_name}, flags={interface_info.flags}),\n"
            py_string += f"    )\n"

        # `NamedVariant` class needs a special parsing method with access to its own specific Havok types module,
        # done here with `globals()`.
        if py_name == "hkRootLevelContainerNamedVariant":
            py_string += "\n".join([
                "",
                "    @classmethod",
                "    def unpack(cls, reader: BinaryReader, offset: int, items: list[TagFileItem] = None) -> hk:",
                "        reader.seek(offset)",
                "        return unpack_named_variant(cls, reader, items, globals())",
                "",
                "    @classmethod",
                "    def unpack_packfile(cls, entry: PackFileItemEntry, offset: int = None, pointer_size=8) -> hk:",
                "        if offset is not None:",
                "            entry.reader.seek(offset)",
                "        return unpack_named_variant_packfile(cls, entry, pointer_size, globals())",
                "",
            ])

        return py_string

    def get_parent_string(self):
        return (
            # f"{self.parent_type_index} | "
            f"{self.parent_type_info.name if self.parent_type_info else None} | "
            f"{self.parent_type_py_name if self.parent_type_py_name else None}"
        )

    def get_pointer_string(self):
        return (
            # f"{self.pointer_type_index} | "
            f"{self.pointer_type_info.name if self.pointer_type_info else None} | "
            f"{self.pointer_type_py_name if self.pointer_type_py_name else None}"
        )

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
