from __future__ import annotations

__all__ = ["PyDefBuilder"]

import re
import typing as tp

from soulstruct_havok.enums import TagDataType, MemberFlags
from .exceptions import HavokTypeError, TypeNotDefinedError

if tp.TYPE_CHECKING:
    from .info import TypeInfo


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

        py_string = (
            f"@dataclass(slots=True, eq=False, repr=False, kw_only=True)\n"
            f"class {self.py_name}({parent_name}):\n"
        )

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
                    py_string += f"        TemplateType(\"{template_info.name}\", _type={template_type_py_name}),\n"
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
