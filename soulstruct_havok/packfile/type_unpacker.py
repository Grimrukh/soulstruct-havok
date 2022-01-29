from __future__ import annotations

import typing as tp

from soulstruct_havok.enums import PackMemberType, TagFormatFlags, TagDataType
from soulstruct_havok.types.core import get_py_name, TypeInfo, MemberInfo

if tp.TYPE_CHECKING:
    from .unpacker import PackFileTypeEntry


_DEBUG_MSG = False


def _DEBUG(*args, **kwargs):
    if _DEBUG_MSG:
        print(*args, **kwargs)


class PackFileTypeUnpacker:
    """Unpacks type entries into `TypeInfo` instances and assigns `py_class` to them.

    TODO: Completely broken, mid-transition. Need to construct `TypeInfo` for each type. Theoretically not that hard,
     I'm just lazy and it's not needed unless I encounter new types I need to examine.

    TODO:
        - Most of the spaghetti here is (a) debug printing or (b) creating generic types manually, neither of which
        needs doing at this point (the debug printing can at least go in a method).
        - All I need to do is read type info, read member info, and retrieve member primitives based on their special
        packfile type enums.
        - I'll need a new `hk` base type for the weird "local struct" thing, which stores `(count, local_offset)`
        for data.
    """

    class EnumValues(dict[str, int]):

        def __init__(self, name: str, items: tp.Sequence[tuple[str, int]]):
            super().__init__()
            self.name = name
            for item in items:
                self[item[0]] = item[1]

        def __repr__(self):
            items = ", ".join(f"{k}={v}" for k, v in self.items())
            return f"{self.name}({items})"

    def __init__(
            self,
            type_entries: list[PackFileTypeEntry],
            type_hashes: dict[str, int],
            pointer_size: int,
            hk_types_module=None,
    ):
        self.type_entries = type_entries
        self.type_hashes = type_hashes
        self.pointer_size = pointer_size
        self.hk_types_module = hk_types_module

        self.enum_dicts = {}  # type: dict[int, PackFileTypeUnpacker.EnumValues]  # maps enum entry indices to value dict

        # TODO: Not using these types here yet, so index doesn't matter.
        # self.hk_type_infos = [None] * (len(self.type_entries) + 1)  # type: list[None | TypeInfo]  # one-indexed
        self.hk_type_infos = []  # type: list[TypeInfo]

        self.observed_member_flags = {}

        for entry in self.type_entries:
            # TODO: What about other types? Just generic?
            if entry.class_name == "hkClass":
                entry.start_reader()
                self.hk_type_infos.append(self.unpack_class_type(entry))

        # TODO: Assign member type infos.
        # for type_info in self.hk_type_infos:
        #     for member in type_info.members:
        #         try:
        #             member.type_info = [t for t in self.hk_type_infos if t.py_name == member.type_py_name][0]
        #         except IndexError:
        #             print([t.name for t in self.hk_type_infos])
        #             print(f"Cannot find member type: {member.type_py_name}")
        #             raise

    def unpack_class_type(self, entry: PackFileTypeEntry):
        if self.pointer_size == 4:
            class_type_header = entry.reader.unpack_struct(entry.NODE_TYPE_STRUCT_32)
        else:
            class_type_header = entry.reader.unpack_struct(entry.NODE_TYPE_STRUCT_64)

        name = entry.reader.unpack_string(offset=entry.child_pointers[0], encoding="utf-8")
        type_info = TypeInfo(name)

        parent_type_entry = entry.get_referenced_entry_type(0 + self.pointer_size)
        if parent_type_entry:
            type_info.parent_type_index = self.type_entries.index(parent_type_entry) + 1
        else:
            type_info.parent_type_index = 0

        # Names of enums defined (redundantly) in the class are recorded for future byte-perfect writes. I don't think
        # it's necessary for the file to be valid, though.
        class_enums = {}  # type: dict[str, PackFileTypeUnpacker.EnumValues]
        if class_type_header["enums_count"]:
            enums_offset = entry.child_pointers[16 if self.pointer_size == 4 else 24]
            with entry.reader.temp_offset(enums_offset):
                enum_dict = self.unpack_enum_type(entry, align_before_name=False, enum_offset=enums_offset)
                if enum_dict.name in class_enums:
                    raise AssertionError(f"Enum {enum_dict.name} was defined more than once in class {name}.")
                class_enums[enum_dict.name] = enum_dict  # for member use

        type_info.members = []
        member_data_offset = entry.child_pointers.get(24 if self.pointer_size == 4 else 40)
        if member_data_offset is not None:
            with entry.reader.temp_offset(member_data_offset):
                for _ in range(class_type_header["member_count"]):
                    member_offset = entry.reader.position
                    if self.pointer_size == 4:
                        member = entry.reader.unpack_struct(entry.NODE_TYPE_MEMBER_STRUCT_32)
                    else:
                        member = entry.reader.unpack_struct(entry.NODE_TYPE_MEMBER_STRUCT_64)
                    member_name_offset = entry.child_pointers[member_offset]
                    member_name = entry.reader.unpack_string(offset=member_name_offset, encoding="utf-8")
                    _DEBUG(f"Member \"{member_name}\"")
                    member_super_and_data_types = member["member_super_and_data_types"]
                    try:
                        member_super_type = PackMemberType.get_data_type(member_super_and_data_types)
                        member_data_type = PackMemberType.get_pointer_type(member_super_and_data_types)
                    except ValueError:
                        raise ValueError(
                            f"Member {member_name} of type {name} has unknown super/data type: "
                            f"{member_super_and_data_types:016b}"
                        )
                    _DEBUG(f"  {member_super_type.name} | {member_data_type.name}")

                    self.observed_member_flags.setdefault(member['flags'], []).append(member_name)

                    member_type_entry = entry.get_referenced_entry_type(member_offset + self.pointer_size)

                    enum_dict = None  # will only be set for enum members

                    if member_super_type == PackMemberType.hkArray:
                        if member_data_type == PackMemberType.hkClass:
                            type_py_name = f"hkArray[{get_py_name(member_type_entry.get_type_name())}]"
                        elif member_data_type == PackMemberType.Ptr:
                            # TODO: How to tell when to use `hkRefPtr`? (Doesn't actually affect unpack anyway?)
                            type_py_name = f"hkArray[Ptr[{get_py_name(member_type_entry.get_type_name())}]]"
                        else:
                            # TODO: Need to add underscore to "_void"
                            type_py_name = f"hkArray[{member_data_type.name}]"  # e.g. "hkArray[hkReal]"

                    elif member_super_type == PackMemberType.NewStruct:
                        # TODO: Add `hkShortPtr` wrapper class to types_base.
                        type_py_name = f"NewStruct[{member_data_type.name}]"  # e.g. "NewStruct[hkVector4f]"

                    elif member_super_type == PackMemberType.hkClass:
                        # `member_type_index` is already correct (no pointers).
                        if member_data_type != PackMemberType.void:
                            raise AssertionError(f"Found non-void data type for Class member {member_name}.")
                        type_py_name = get_py_name(member_type_entry.get_type_name())

                    elif member_super_type == PackMemberType.Ptr:
                        if member_data_type == PackMemberType.hkClass:
                            type_py_name = f"Ptr[{get_py_name(member_type_entry.get_type_name())}]"
                            pass  # `member_type_index` is correct
                        elif member_data_type == PackMemberType.void:
                            type_py_name = "Ptr[_void]"
                        else:
                            raise AssertionError(f"Invalid data type for Ptr: {member_data_type.name}")

                    elif member_super_type in {PackMemberType.hkEnum, PackMemberType.hkFlags}:
                        # TODO: `hkFlags` occurs in 2014. Not sure how it differs to `hkEnum`, or it its type should
                        #  be named differently.
                        enum_offset = member_offset + (8 if self.pointer_size == 4 else 16)
                        enum_entry = entry.get_referenced_entry_type(enum_offset)
                        # TODO: no actual enum names here.
                        # type_py_name = f"hkEnum[{get_py_name(enum_entry.get_type_name())}]"
                        type_py_name = f"hkEnum[{member_data_type.name}]"

                    else:
                        if member_data_type != PackMemberType.void:
                            raise AssertionError(f"Found non-void data type for primitive member {member_name}.")
                        type_py_name = member_super_type.name  # primitive

                    # `hkStruct` indication is simply that "c_array_size" is greater than zero; the type just defined
                    # above goes inside a struct.
                    if member["c_array_size"] > 0:
                        type_py_name = f"hkStruct[{type_py_name}]"

                    # TODO: Do something with enum dict...

                    type_info.members.append(
                        MemberInfo(
                            name=member_name,
                            flags=member["flags"],  # TODO: I believe these are different from tagfile flags.
                            offset=member["member_byte_offset"],
                            type_py_name=type_py_name,
                        )
                    )
                    _DEBUG(f"  -> {type_py_name}")
                    # TODO: Should only be checking module for `hk` names; all hkArray, etc. generics are always fine.
                    # try:
                    #     getattr(self.hk_types_module, py_type_name)
                    # except AttributeError:
                    #     raise TypeError(f"No such Python type `{py_type_name}` for member \"{member_name}\".")

        type_info.pointer_type_index = 0  # only `hkClass` types unpacked here
        type_info.version = class_type_header["version"]
        type_info.byte_size = class_type_header["byte_size"]
        type_info.alignment = min(16, next_power_of_two(class_type_header["byte_size"]))
        # TODO: abstract_value?
        type_info.hsh = self.type_hashes.get(name, 0)
        type_info.tag_format_flags = TagFormatFlags.get_packfile_type_flags(has_version=False)  # all versions are zero
        type_info.tag_type_flags = TagDataType.Class

        return type_info

    def unpack_enum_type(self, entry: PackFileTypeEntry, align_before_name: bool, enum_offset=0) -> EnumValues:
        """Unpack and return an `EnumValues` name -> value dictionary.

        These are packed on their own, as genuine `type_entries`, and are also embedded inside the class entries that
        have members that use them. The genuine ones are simply unpacked and discarded, and the indices where they
        occur are overriden with the real `hkEnum` types created when their members are encountered. The dictionary is
        loaded into the `hkx_enum` attribute of the member (only needed to regenerate the type section properly when
        writing these packfiles).
        """

        if self.pointer_size == 4:
            enum_type_struct = entry.reader.unpack_struct(entry.NODE_TYPE_ENUM_STRUCT_32)
        else:
            enum_type_struct = entry.reader.unpack_struct(entry.NODE_TYPE_ENUM_STRUCT_64)
        if align_before_name:
            entry.reader.align(16)
        name = entry.reader.unpack_string(offset=entry.child_pointers[enum_offset + 0], encoding="utf-8")
        items = []
        _DEBUG(f"   Enum {name}:")
        with entry.reader.temp_offset(entry.child_pointers[enum_offset + self.pointer_size]):
            for _ in range(enum_type_struct["items_count"]):
                item_value = entry.reader.unpack_value("<I" if self.pointer_size == 4 else "<Q")
                item_name_offset = entry.child_pointers[entry.reader.position]
                item_name = entry.reader.unpack_string(offset=item_name_offset, encoding="utf-8")
                entry.reader.unpack_value("<I" if self.pointer_size == 4 else "<Q", asserted=0)
                _DEBUG(f"       {item_name} = {item_value}")
                items.append((item_name, item_value))

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
