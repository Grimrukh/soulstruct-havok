from __future__ import annotations

import typing as tp

from soulstruct_havok.enums import PackMemberType, TagFormatFlags, TagDataType, MemberFlags, PackMemberFlags
from soulstruct_havok.types.info import TypeInfo, MemberInfo, get_py_name

if tp.TYPE_CHECKING:
    from .unpacker import PackFileTypeItem


_DEBUG_MSG = False
_DEBUG_ENUMS = False


def _DEBUG(*args, **kwargs):
    if _DEBUG_MSG:
        print(*args, **kwargs)


def _DEBUG_ENUM(enum_str: str):
    if _DEBUG_ENUMS:
        print(enum_str)


class PackFileTypeUnpacker:
    """Unpacks type entries into `TypeInfo` instances and assigns `py_class` to them."""

    class EnumValues(dict[str, int]):

        def __init__(self, name: str, items: tp.Sequence[tuple[str, int]]):
            super().__init__()
            self.name = name
            for item in items:
                self[item[0]] = item[1]

        def __repr__(self):
            items = ", ".join(f"{k}={v}" for k, v in self.items())
            return f"{self.name}({items})"

    type_items: list[None | PackFileTypeItem]

    def __init__(
        self,
        type_items: list[None | PackFileTypeItem],
        type_hashes: dict[str, int],
        pointer_size: int,
        hk_types_module=None,
    ):
        self.type_items = [None] + type_items  # for one-indexing
        self.type_hashes = type_hashes
        self.pointer_size = pointer_size
        self.hk_types_module = hk_types_module

        print(f"Running `PackFileTypeUnpacker` with pointer size {self.pointer_size}.")

        self.parent_children = {}  # maps Python parent names to lists of Python child names

        # Maps enum names to unpacked dictionaries.
        self.enum_dicts = {}  # type: dict[str, PackFileTypeUnpacker.EnumValues]
        self.enum_storage_types = {}  # type: dict[str, PackMemberType]

        self.type_infos = [None]  # type: list[None | TypeInfo]

        for item in self.type_items[1:]:
            # TODO: What about other types? Just generic?
            if item.class_name == "hkClass":
                item.start_reader()
                self.type_infos.append(self.unpack_type_item(item))

        # Assign `TypeInfo` to members and parents. (Pointer types always zero, as these are only classes.)
        for type_info in self.type_infos[1:]:
            if type_info.parent_type_py_name:
                type_info.parent_type_info = [
                    t for t in self.type_infos[1:] if t.py_name == type_info.parent_type_py_name
                ][0]
            for member in type_info.members:
                try:
                    member.type_info = [t for t in self.type_infos[1:] if t.py_name == member.type_py_name][0]
                except IndexError:
                    if not PackMemberType.is_builtin_type(member.type_py_name):
                        print([t.name for t in self.type_infos[1:]])
                        print(f"Cannot find member type: {member.type_py_name}")
                        raise

        # Create Python enum types.
        for full_enum_name, storage_type in self.enum_storage_types.items():
            # TODO: In tagfiles, the int size of the enum type is not always the same as the int size of the storage
            #  type. Not sure if or how I can detect that different here in packfile types. Using storage type for now.
            enum_type_info = TypeInfo(full_enum_name)
            enum_type_info.tag_type_flags = TagDataType.from_packfile_integer(storage_type)
            if enum_type_info.tag_type_flags & TagDataType.Int8:
                enum_type_info.byte_size = 1
                enum_type_info.alignment = 1
            elif enum_type_info.tag_type_flags & TagDataType.Int16:
                enum_type_info.byte_size = 2
                enum_type_info.alignment = 2
            elif enum_type_info.tag_type_flags & TagDataType.Int32:
                enum_type_info.byte_size = 4
                enum_type_info.alignment = 4
            elif enum_type_info.tag_type_flags & TagDataType.Int64:
                enum_type_info.byte_size = 8
                enum_type_info.alignment = 8
            self.type_infos.append(enum_type_info)

    def unpack_type_item(self, entry: PackFileTypeItem):
        if self.pointer_size == 4:
            type_item_header = entry.TYPE_STRUCT_32.from_bytes(entry.reader)
        else:
            type_item_header = entry.TYPE_STRUCT_64.from_bytes(entry.reader)

        name = entry.reader.unpack_string(offset=entry.child_pointers[0], encoding="utf-8")
        py_name = get_py_name(name)
        type_info = TypeInfo(name)

        _DEBUG(f"Unpacking type: {name}")

        parent_type_entry = entry.get_referenced_type_item(0 + self.pointer_size)  # skip name pointer
        type_info.parent_type_index = self.type_items.index(parent_type_entry)  # could be `None` (-> 0)
        if type_info.parent_type_index > 0:
            type_info.parent_type_py_name = get_py_name(parent_type_entry.get_type_name())
            self.parent_children.setdefault(type_info.parent_type_py_name, []).append(get_py_name(name))

        # Names of enum values defined (redundantly) in the class are recorded for future byte-perfect writes. I don't
        # think it's necessary for the file to be valid, though.
        class_enums = {}  # type: dict[str, PackFileTypeUnpacker.EnumValues]
        if type_item_header.enums_count:
            enums_offset = entry.child_pointers[16 if self.pointer_size == 4 else 24]
            with entry.reader.temp_offset(enums_offset):
                enum_dict = self.unpack_enum_type(entry, align_before_name=False, enum_offset=enums_offset)
                if enum_dict.name in class_enums:
                    raise AssertionError(f"Enum {enum_dict.name} was defined more than once in class {name}.")
                class_enums[enum_dict.name] = enum_dict  # for member use
                self.enum_dicts[f"{name}::{enum_dict.name}"] = enum_dict

        type_info.members = []
        member_data_offset = entry.child_pointers.get(24 if self.pointer_size == 4 else 40)
        if member_data_offset is not None:
            with entry.reader.temp_offset(member_data_offset):
                for _ in range(type_item_header.member_count):
                    member_offset = entry.reader.position
                    if self.pointer_size == 4:
                        member = entry.MEMBER_TYPE_STRUCT.from_bytes(entry.reader, long_varints=False)
                    else:
                        member = entry.MEMBER_TYPE_STRUCT.from_bytes(entry.reader, long_varints=True)
                    member_name_offset = entry.child_pointers[member_offset]
                    member_name = entry.reader.unpack_string(offset=member_name_offset, encoding="utf-8")
                    _DEBUG(f"    Member \"{member_name}\" ({member_offset} | {hex(member_offset)}) ({member.flags})")
                    member_type = PackMemberType(member.member_type)
                    member_subtype = PackMemberType(member.member_subtype)
                    _DEBUG(f"      {member_type.name} | {member_subtype.name}")
                    member_type_item = entry.get_referenced_type_item(member_offset + self.pointer_size)

                    if member_type == PackMemberType.TYPE_ARRAY:
                        if member_subtype == PackMemberType.TYPE_STRUCT:
                            type_py_name = f"hkArray[{get_py_name(member_type_item.get_type_name())}]"
                            member_py_name = f"hkArray({get_py_name(member_type_item.get_type_name())})"
                            type_hint = f"list[{get_py_name(member_type_item.get_type_name())}]"
                            required_types = [get_py_name(member_type_item.get_type_name())]
                        elif member_subtype == PackMemberType.TYPE_POINTER:
                            if member_type_item is None:  # invalid
                                type_py_name = "hkArray[hkReflectDetailOpaque]"
                                member_py_name = "hkArray(hkReflectDetailOpaque)"
                                type_hint = "list"
                                required_types = ["hkReflectDetailOpaque"]
                            else:
                                # TODO: How to tell when to use `hkRefPtr`? (Doesn't actually affect unpack anyway?)
                                class_name = get_py_name(member_type_item.get_type_name())
                                type_py_name = f"hkArray[Ptr[{class_name}]]"
                                if member.flags & PackMemberFlags.NOT_OWNED:  # `hkViewPtr`
                                    member_py_name = f"hkArray(Ptr(hkViewPtr(\"{class_name}\")))"
                                    # Class name not required.
                                elif class_name == py_name:
                                    # Need `DefType`.
                                    member_py_name = f"hkArray(Ptr(DefType(\"{class_name}\", lambda: {class_name})))"
                                    # Class name not required.
                                else:
                                    member_py_name = f"hkArray(Ptr({class_name}))"
                                    required_types = [class_name]
                                type_hint = f"list[{class_name}]"

                        elif member_subtype == PackMemberType.TYPE_VOID:
                            type_py_name = f"hkArray[hkReflectDetailOpaque]"
                            member_py_name = "hkArray(hkReflectDetailOpaque)"
                            type_hint = "list"
                            required_types = ["hkReflectDetailOpaque"]
                        else:
                            type_py_name = f"hkArray[{member_subtype.get_py_type_name()}]"
                            member_py_name = f"hkArray({member_subtype.get_py_type_name()})"
                            type_hint = f"list[{member_subtype.get_true_py_type_name()}]"
                            required_types = [member_subtype.get_py_type_name()]

                    elif member_type == PackMemberType.TYPE_RELARRAY:
                        if member_subtype == PackMemberType.TYPE_STRUCT:
                            # Array of class instances.
                            class_name = get_py_name(member_type_item.get_type_name())
                            type_py_name = f"hkRelArray[{class_name}]"
                            member_py_name = f"hkRelArray({class_name})"
                            type_hint = f"list[{class_name}]"
                            required_types = [class_name]
                        else:
                            # Array of primitives.
                            type_py_name = f"hkRelArray[{member_subtype.get_py_type_name()}]"
                            member_py_name = f"hkRelArray({member_subtype.get_py_type_name()})"
                            type_hint = f"list[{member_subtype.get_true_py_type_name()}]"
                            required_types = [member_subtype.get_py_type_name()]

                    elif member_type == PackMemberType.TYPE_STRUCT:
                        # `member_type_index` is already correct (no pointers).
                        if member_subtype != PackMemberType.TYPE_VOID:
                            raise AssertionError(f"Found non-void data type for Class member {member_name}.")
                        type_py_name = member_py_name = type_hint = get_py_name(member_type_item.get_type_name())
                        required_types = [member_py_name]

                    elif member_type == PackMemberType.TYPE_POINTER:
                        if member_subtype == PackMemberType.TYPE_STRUCT:
                            # `member_type_index` is already correct.
                            class_name = get_py_name(member_type_item.get_type_name())
                            type_py_name = f"Ptr[{class_name}]"
                            # TODO: Check for hkViewPtr (member flags).
                            class_is_child = False
                            children = self.parent_children.get(py_name, []).copy()
                            while children:
                                child = children.pop()
                                if class_name == child:
                                    class_is_child = True
                                    break
                                children += self.parent_children.get(child, []).copy()
                            if class_name == py_name or class_is_child:
                                # Need `DefType`.
                                member_py_name = f"Ptr(DefType(\"{class_name}\", lambda: {class_name}))"
                                # Class name is not a required type.
                            else:
                                member_py_name = f"Ptr({class_name})"
                                required_types = [class_name]
                            type_hint = class_name
                        elif member_subtype == PackMemberType.TYPE_VOID:
                            type_py_name = "Ptr[hkReflectDetailOpaque]"
                            member_py_name = "Ptr(hkReflectDetailOpaque)"
                            type_hint = "None"
                            required_types = ["hkReflectDetailOpaque"]
                        else:
                            raise AssertionError(f"Invalid data type for Ptr: {member_subtype.name}")

                    elif member_type == PackMemberType.TYPE_ENUM:
                        enum_offset = member_offset + (8 if self.pointer_size == 4 else 16)
                        enum_type_item = entry.get_referenced_type_item(enum_offset)
                        storage_type_name = member_subtype.get_py_type_name()
                        if enum_type_item:
                            full_enum_name = f"{name}::{enum_type_item.get_type_name()}"
                            enum_type_name = get_py_name(full_enum_name)
                            self.enum_storage_types[full_enum_name] = member_subtype
                        else:
                            if name == "hkaAnimatedReferenceFrame" and member_name == "frameType":
                                # TODO: Weird missing enum sometimes. Filling in manually.
                                full_enum_name = f"{name}::hkaReferenceFrameTypeEnum"
                            elif name == "hkpShape" and member_name == "type":
                                # TODO: Old member with no enum data. Probably superseded by `hkcdShapeType`.
                                full_enum_name = f"{name}::ShapeType"  # GUESS
                            else:
                                raise ValueError(f"No enum type for member '{member_name}' of `{name}`.")
                            enum_type_name = get_py_name(full_enum_name)
                            self.enum_storage_types[full_enum_name] = member_subtype
                        type_py_name = f"hkEnum[{enum_type_name}, {storage_type_name}]"
                        member_py_name = f"hkEnum({enum_type_name}, {storage_type_name})"
                        type_hint = member_subtype.get_true_py_type_name()
                        required_types = [enum_type_name, storage_type_name]

                    elif member_type == PackMemberType.TYPE_FLAGS:
                        # storage_offset = member_offset + (8 if self.pointer_size == 4 else 16)
                        # storage_type_item = entry.get_referenced_type_item(storage_offset)
                        type_py_name = f"hkFlags[{member_subtype.get_py_type_name()}]"
                        member_py_name = f"hkFlags({member_subtype.get_py_type_name()})"
                        type_hint = member_subtype.get_true_py_type_name()
                        required_types = [member_subtype.get_py_type_name()]

                    else:  # primitive (subtype must be `TYPE_VOID`)
                        if member_subtype != PackMemberType.TYPE_VOID:
                            raise AssertionError(
                                f"Non-void subtype for primitive member {member_name}: {member_subtype}"
                            )
                        type_py_name = member_py_name = member_type.get_py_type_name()  # primitive
                        type_hint = member_type.get_true_py_type_name()
                        required_types = [member_type.get_py_type_name()]

                    # `hkStruct` indication is simply that "c_array_size" is greater than zero; the type just defined
                    # above goes inside a struct.
                    if member.c_array_size > 0:
                        type_py_name = f"hkStruct[{type_py_name}]"
                        member_py_name = f"hkStruct({member_py_name}, {member.c_array_size})"
                        type_hint = f"tuple[{type_hint}, ...]"

                    member_info = MemberInfo(
                        name=member_name,
                        flags=MemberFlags.from_packfile_member_flags(member.flags),
                        offset=member.offset,
                        type_py_name=type_py_name,
                        # `TypeInfo` of member assigned after all type items unpacked.
                    )
                    # TODO: Secret attributes for module generation. Should be made official.
                    member_info.member_py_name = member_py_name
                    member_info.type_hint = type_hint
                    member_info.required_types = required_types
                    type_info.members.append(member_info)
                    _DEBUG(f"      -> {type_py_name}")
                    # TODO: Should only be checking module for non-generic names. And should only WARN, not error out.
                    # try:
                    #     getattr(self.hk_types_module, py_type_name)
                    # except AttributeError:
                    #     raise TypeError(f"No such Python type `{py_type_name}` for member \"{member_name}\".")

        type_info.pointer_type_index = 0  # only `hkClass` types are ever unpacked here and never have a pointer type
        type_info.version = type_item_header.version if type_item_header.version > 0 else None
        type_info.byte_size = type_item_header.byte_size
        # TODO: Can I use member flags to help with alignment?
        type_info.alignment = min(16, next_power_of_two(type_item_header.byte_size))
        # TODO: abstract_value?
        type_info.hsh = self.type_hashes.get(name, None)
        type_info.tag_format_flags = TagFormatFlags.get_packfile_type_flags(has_version=False)  # all versions are zero
        type_info.tag_type_flags = TagDataType.Class

        return type_info

    def unpack_enum_type(self, enum_type_item: PackFileTypeItem, align_before_name: bool, enum_offset=0) -> EnumValues:
        """Unpack and return an `EnumValues` name -> value dictionary.

        These are packed on their own, as genuine `type_entries`, and are also embedded inside the class entries that
        have members that use them. The genuine ones are simply unpacked and discarded, and the indices where they
        occur are overriden with the real `hkEnum` types created when their members are encountered. The dictionary is
        loaded into the `hkx_enum` attribute of the member (only needed to regenerate the type section properly when
        writing these packfiles).
        """

        if self.pointer_size == 4:
            enum_type_struct = enum_type_item.ENUM_TYPE_STRUCT.from_bytes(enum_type_item.reader, long_varints=False)
        else:
            enum_type_struct = enum_type_item.ENUM_TYPE_STRUCT.from_bytes(enum_type_item.reader, long_varints=True)
        if align_before_name:
            enum_type_item.reader.align(16)
        name = enum_type_item.reader.unpack_string(
            offset=enum_type_item.child_pointers[enum_offset + 0], encoding="utf-8"
        )
        items = []
        enum_str = f"class {name}(IntEnum):\n"
        with enum_type_item.reader.temp_offset(enum_type_item.child_pointers[enum_offset + self.pointer_size]):
            for _ in range(enum_type_struct.items_count):
                item_value = enum_type_item.reader.unpack_value("<I" if self.pointer_size == 4 else "<Q")
                item_name_offset = enum_type_item.child_pointers[enum_type_item.reader.position]
                item_name = enum_type_item.reader.unpack_string(offset=item_name_offset, encoding="utf-8")
                enum_type_item.reader.unpack_value("<I" if self.pointer_size == 4 else "<Q", asserted=0)
                enum_str += f"    {item_name} = {item_value}\n"
                items.append((item_name, item_value))

        _DEBUG_ENUM(enum_str)

        return PackFileTypeUnpacker.EnumValues(name, items)


def next_power_of_two(n) -> int:
    if n == 1:
        return 2
    n -= 1
    n |= n >> 1
    n |= n >> 2
    n |= n >> 4
    n |= n >> 8
    n |= n >> 16
    n += 1
    return n
