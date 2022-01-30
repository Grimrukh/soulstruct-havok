"""Classes for representing direct information about a Havok type unpacked from, or to be packed to, a file."""
from __future__ import annotations

__all__ = [
    "HAVOK_TYPE_PREFIXES",
    "HavokTypeError",
    "TypeNotDefinedError",
    "TypeMatchError",
    "TemplateInfo",
    "MemberInfo",
    "InterfaceInfo",
    "TypeInfo",
    "get_py_name",
]

import re
import typing as tp

from soulstruct_havok.enums import TagDataType

if tp.TYPE_CHECKING:
    from .core import hk


class HavokTypeError(Exception):
    """Raised by any error caused by missing, invalid, or malformed Havok types."""


class TypeNotDefinedError(HavokTypeError):
    """Raised when an undefined parent or member is encountered."""


class TypeMatchError(HavokTypeError):
    """Raised when a Python class's information clashes with a new `TypeInfo`."""
    def __init__(self, py_class: tp.Type[hk], field_name: str, py_value, new_value):
        super().__init__(
            f"Python type `{py_class.__name__}` has {field_name} = {py_value}, but this `TypeInfo` has "
            f"{field_name} = {new_value}."
        )


# Any type whose real Havok name does not start with one of these will have an underscore prepended to its Python name.
HAVOK_TYPE_PREFIXES = ("hk", "hcl", "Custom")


def get_py_name(real_name: str) -> str:
    py_name = real_name.replace("::", "").replace(" ", "_").replace("*", "")
    if not any(py_name.startswith(s) for s in HAVOK_TYPE_PREFIXES):
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

        # Deindexified attributes.
        self.type_info = type_info
        self.type_py_name = type_py_name

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
                if py_member.type is None:
                    raise ValueError(f"Defined Member {py_member.name} has type None. TypeInfo: {self}")

            # TODO: Should also check member type, but that's a little more complex with the array/enum wrappers, etc.

    def get_class_py_def(self, defined_type_names: list[str]) -> str:
        return PyDefBuilder(self, defined_type_names).build()

    def get_parent_string(self):
        return (
            f"{self.parent_type_info.name if self.parent_type_info else None} | "
            f"{self.parent_type_py_name if self.parent_type_py_name else None}"
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
                py_def += (
                    f"        Member(\"{member.name}\", {member.type_py_name}, "
                    f"offset={member.offset}, flags={member.flags}),\n"
                )
            py_def += "    )"

        # TODO: templates, interfaces

        return py_def

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
    defined_type_names: list[str]

    def __init__(self, type_info: TypeInfo, defined_type_names: list[str]):
        self.info = type_info
        self.defined_type_names = defined_type_names + [type_info.name]  # may reference self

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

    def build_new_struct_type(self, new_struct_type: TypeInfo) -> tuple[str, str]:
        struct_data_type = new_struct_type.pointer_type_info
        py_name, type_hint = self.build_type_name(struct_data_type)
        return f"NewStruct({py_name})", f"tuple[{type_hint}]"

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
        if data_type_info.py_name not in self.defined_type_names:
            raise TypeNotDefinedError(f"Undefined data type for `hkRefVariant`: {data_type_info.py_name}`")
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
        if data_type_info.py_name not in self.defined_type_names:
            raise TypeNotDefinedError(f"Undefined data type for `hkRefPtr`: {data_type_info.py_name}`")
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
        if data_type_info.py_name not in self.defined_type_names:
            raise TypeNotDefinedError(f"Undefined data type for `Ptr`: {data_type_info.py_name}`")
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
            if py_name not in self.defined_type_names:
                raise TypeNotDefinedError(f"Undefined data type for `hkStruct`: {py_name}`")
        return f"hkGenericStruct({py_name}, {struct_length})", f"tuple[{type_hint}]"

    def build_enum_type(self, enum_type: TypeInfo) -> tuple[str, str]:
        t_enum_type = enum_type.templates[0].type_info  # "tENUM" template
        t_storage_type = enum_type.templates[1].type_info  # "tSTORAGE" template
        if t_enum_type.py_name not in self.defined_type_names:
            raise TypeNotDefinedError(f"Undefined enum type for `hkEnum`: {t_enum_type.py_name}`")
        if t_storage_type.py_name not in self.defined_type_names:
            raise TypeNotDefinedError(f"Undefined storage type for `hkEnum`: {t_storage_type.py_name}`")
        return f"hkEnum({t_enum_type.py_name}, {t_storage_type.py_name})", t_enum_type.py_name

    def build_type_name(self, type_info: TypeInfo, allow_undefined=False) -> tuple[str, str]:
        """Determine Python type for member definition.

        Returns both the true type string (for packing/unpacking), e.g. `hkArray(Ptr(hkaSkeleton))`, and the type hint
        for the Python object that will actually represent this member, e.g. `list[hkaSkeleton]`.
        """

        # TODO: Determine how 'NewStruct' will be detected properly from 2014 packfiles.
        if self.py_name in {"hknpConvexShape", "hknpConvexPolytopeShape"}:
            # All members are `NewStruct` but are incorrectly stored as `hkArray` in the XML.
            return self.build_new_struct_type(type_info)

        if type_info.name == "hkArray":
            return self.build_array_type(type_info)
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
                if "hkReflectQualifiedType" not in self.defined_type_names:
                    raise TypeNotDefinedError("Undefined pointer type name: hkReflectQualifiedType")
                return "hkReflectQualifiedType", "hkReflectQualifiedType"
            elif type_info.name == "hkPropertyBag":
                if "hkPropertyBag" not in self.defined_type_names:
                    raise TypeNotDefinedError("Undefined pointer type name: hkPropertyBag")
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
            # Primitive type.
            if not allow_undefined and type_info.py_name not in self.defined_type_names:
                raise TypeNotDefinedError(f"Undefined primitive/class member type: {type_info.py_name}")
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
                if parent_name not in self.defined_type_names:
                    raise TypeNotDefinedError(f"Undefined parent for `{self.name}`: `{parent_name}`")
            elif self.info.pointer_type_info is not None and self.info.name not in {"T*", "hkRefPtr", "hkRefVariant"}:
                parent_name = "hkBasePointer"
            else:
                parent_name = "hk"

        py_string = f"class {self.py_name}({parent_name}):\n"

        if self.tag_type_flags is None and self.name != "void":
            # Bare alias wrapper. Just define hash and empty members.
            assert (self.info.alignment is None)
            assert (self.info.byte_size is None)
            assert (self.info.tag_format_flags == 0)
            py_string += "    \"\"\"Havok alias.\"\"\"\n"
            if self.info.hsh:
                py_string += f"    __hsh = {self.info.hsh}\n"
            py_string += "    __tag_format_flags = 0\n"
            py_string += "    local_members = ()\n"
            return py_string

        for field in ("alignment", "byte_size", "tag_type_flags"):
            py_string += f"    {field} = {getattr(self.info, field)}\n"

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
                print(f"  Member {member.name} (type {member.type_info.name})")
                py_name, type_hint = self.build_type_name(member.type_info)
                print(f"    --> {py_name} | {type_hint}")
                member_string = f"        Member({member.offset}, \"{member.name}\", {py_name}"
                member_string += f", flags={member.flags}),\n" if member.flags != 32 else "),\n"
                if len(member_string) > self.MAX_LINE_LENGTH - 8:  # account for indent
                    # Reformat with line breaks.
                    member_string = (
                        f"        Member(\n"
                        f"            {member.offset},\n"
                        f"            \"{member.name}\",\n"
                        f"            {py_name},\n"
                    )
                    member_string += f"            flags={member.flags},\n" if member.flags != 32 else ""
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
                py_string += f"        Interface({interface_type_py_name}, flags={interface_info.flags}),\n"
            py_string += f"    )\n"

        return py_string
