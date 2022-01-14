from __future__ import annotations

__all__ = ["PackFileUnpacker"]

import logging
import typing as tp

from soulstruct.utilities.binary import BinaryReader

from soulstruct_havok.enums import PackMemberType, TagDataType, TagFormatFlags
from soulstruct_havok.types.core import hk
from soulstruct_havok.types.info import TypeInfo, MemberInfo, get_py_name
from .structs import *

_LOGGER = logging.getLogger(__name__)

_DEBUG_PRINT = []
_DEBUG_TYPE_PRINT = False


class SectionInfo(tp.NamedTuple):
    raw_data: bytes
    child_pointers: list[dict[str, int]]
    entry_pointers: list[dict[str, int]]
    entry_specs: list[dict[str, int]]
    end_offset: int


class PackFileUnpacker:

    items: list[PackFileItemEntry]
    hk_version: str
    hk_types_info: list[TypeInfo]
    root: hk

    def __init__(self):
        self.hk_types_module = None
        # TODO: define attrs

    def unpack(self, reader: BinaryReader, types_only=False):

        self.byte_order = reader.byte_order = "<" if reader.unpack_value("?", offset=0x11) else ">"
        self.header = PackFileHeader(reader)

        self.hk_version = self.header.contents_version_string[3:7].decode()  # from "hk_YYYY" (e.g. "2010")

        if self.header.version.has_header_extension:
            header_extension = PackFileHeaderExtension(reader)
            reader.seek(header_extension.section_offset + 0x40)
        elif reader.unpack_value("I") != 0xFFFFFFFF:
            raise ValueError(f"Expected 0xFFFFFFFF after packfile header (version {hex(self.header.version)}).")

        if self.header.pointer_size not in {4, 8}:
            raise ValueError(f"Packfile pointer size must be 4 or 8, not {self.header.pointer_size}.")

        type_name_info = self.unpack_section(reader)
        if type_name_info.child_pointers:
            raise AssertionError("Type name section has local references. Not expected!")
        if type_name_info.entry_pointers:
            raise AssertionError("Type name section has global references. Not expected!")
        if type_name_info.entry_specs:
            raise AssertionError("Type name section has data entries. Not expected!")

        type_section_info = self.unpack_section(reader)
        for type_section_entry_pointer in type_section_info.entry_pointers:
            if type_section_entry_pointer["dest_section_index"] != 1:
                raise AssertionError("type global error")

        data_section_info = self.unpack_section(reader)

        self.unpack_class_names(BinaryReader(type_name_info.raw_data))

        self.type_entries = self.unpack_type_entries(
            BinaryReader(type_section_info.raw_data),
            entry_specs=type_section_info.entry_specs,
            section_end_offset=type_section_info.end_offset
        )
        self.localize_pointers(
            self.type_entries,
            type_section_info.child_pointers,
            type_section_info.entry_pointers,
        )

        if self.type_entries:
            # Types defined inside file, minus some primitive types that are supplied manually.
            self.hk_type_infos = TypeUnpacker(
                self.type_entries, self.class_hashes, self.header.pointer_size, self.hk_types_module
            ).hk_type_infos

        if types_only:
            # All missing (primitive) types must be present in `hk2014_base`.
            from soulstruct_havok.types import hk2014_base
            for type_info in self.hk_type_infos:
                for member in type_info.members:
                    try:
                        member_hk_type = [t for t in self.hk_type_infos if t.py_name == member.type_py_name][0]
                    except IndexError:
                        try:
                            member_hk_type = getattr(hk2014_base, member.type_py_name)
                        except AttributeError:
                            raise AttributeError(f"Could not find Havok 2014 type `{member.type_py_name}`.")
                    member.type_info = member_hk_type.get_type_info()
            return

        # TODO: Just loading 2014 for now.
        from soulstruct_havok.types import hk2014, hk2014_base
        self.hk_types_module = hk2014

        # for type_info in self.hk_type_infos:
        #     for member in type_info.members:
        #         try:
        #             member_hk_type = getattr(self.hk_type_infos, member.type_py_name)
        #         except AttributeError:
        #             # Use `hk2014_base` as a backup.
        #             try:
        #                 member_hk_type = getattr(hk2014_base, member.type_py_name)
        #             except AttributeError:
        #                 raise AttributeError(f"Could not find Havok 2014 type `{member.type_py_name}`.")
        #         member.type_info = member_hk_type.get_type_info()

        self.items = self.unpack_item_entries(
            BinaryReader(data_section_info.raw_data),
            entry_specs=data_section_info.entry_specs,
            section_end_offset=data_section_info.end_offset,
        )
        self.localize_pointers(
            self.items,
            data_section_info.child_pointers,
            data_section_info.entry_pointers,
        )

        root_entry = self.items[0]
        if root_entry.hk_type != self.hk_types_module.hkRootLevelContainer:
            raise TypeError(f"First data entry in HKX was not root node: {root_entry.hk_type.__name__}")
        root_entry.start_reader()
        self.root = self.hk_types_module.hkRootLevelContainer.unpack_packfile(
            root_entry, pointer_size=self.header.pointer_size
        )

    @staticmethod
    def localize_pointers(
        entries: tp.Union[list[PackFileTypeEntry], list[PackFileItemEntry]],
        child_pointers: list[dict[str, int]],
        entry_pointers: list[dict[str, int]],
    ):
        """Resolve pointers and attach them to their source objects."""
        for child_pointer in child_pointers:
            # Find source object and offset local to its data.
            for entry in entries:
                if (entry_source_offset := entry.get_offset_in_entry(child_pointer["source_offset"])) != -1:
                    # Check that source object is also dest object.
                    if (entry_dest_offset := entry.get_offset_in_entry(child_pointer["dest_offset"])) == -1:
                        raise AssertionError("Child pointer source object was NOT dest object. Not expected!")
                    entry.child_pointers[entry_source_offset] = entry_dest_offset
                    break
            else:
                raise ValueError(f"Could not find source/dest entry of child pointer: {child_pointer}.")

        for entry_pointer in entry_pointers:
            for entry in entries:
                if (entry_source_offset := entry.get_offset_in_entry(entry_pointer["source_offset"])) != -1:
                    source_entry = entry
                    break
            else:
                raise ValueError(f"Could not find source entry of entry pointer: {entry_pointer}.")
            for entry in entries:
                if (entry_dest_offset := entry.get_offset_in_entry(entry_pointer["dest_offset"])) != -1:
                    source_entry.entry_pointers[entry_source_offset] = (entry, entry_dest_offset)
                    break
            else:
                raise ValueError(f"Could not find dest entry of entry pointer: {entry_pointer}.")

    def unpack_section(self, reader: BinaryReader) -> SectionInfo:
        """Section structure is:

            - Packed section data (e.g. class name strings or packed entries).
            -
        """
        section = PackFileSectionHeader(reader)

        if self.hk_version == "2014":
            if reader.read(16).strip(b"\xFF"):
                raise AssertionError("Expected sixteen 0xFF bytes after section header in HKX packfile version 2014.")

        absolute_data_start = section.absolute_data_start
        section_data_end = section.child_pointers_offset
        section_data = reader.unpack_bytes(length=section_data_end, offset=absolute_data_start, strip=False)
        child_pointer_count = (section.entry_pointers_offset - section.child_pointers_offset) // 8
        entry_pointer_count = (section.entry_specs_offset - section.entry_pointers_offset) // 12
        entry_spec_count = (section.exports_offset - section.entry_specs_offset) // 12

        child_pointers = []
        entry_pointers = []
        entry_specs = []

        with reader.temp_offset(offset=absolute_data_start + section.child_pointers_offset):
            for _ in range(child_pointer_count):
                if reader.unpack_value("I", offset=reader.position) == 0xFFFFFFFF:
                    break  # padding reached
                child_pointers.append(reader.unpack_struct(CHILD_POINTER_STRUCT))
        with reader.temp_offset(offset=absolute_data_start + section.entry_pointers_offset):
            for _ in range(entry_pointer_count):
                if reader.unpack_value("I", offset=reader.position) == 0xFFFFFFFF:
                    break  # padding reached
                entry_pointers.append(reader.unpack_struct(ENTRY_POINTER_STRUCT))
        with reader.temp_offset(offset=absolute_data_start + section.entry_specs_offset):
            for _ in range(entry_spec_count):
                if reader.unpack_value("I", offset=reader.position) == 0xFFFFFFFF:
                    break  # padding reached
                entry_specs.append(reader.unpack_struct(ENTRY_SPEC_STRUCT))

        return SectionInfo(section_data, child_pointers, entry_pointers, entry_specs, section_data_end)

    def unpack_class_names(self, type_name_reader: BinaryReader):
        """Returns a dictionary mapping offsets (within class name section) to HKX class names and signatures."""
        self.class_names = {}
        self.class_hashes = {}

        while type_name_reader.peek_value("H") != 0xFFFF:
            hsh = type_name_reader.unpack_value("I")
            type_name_reader.unpack_value("B", asserted=0x09)  # \t (tab character)
            type_name_offset = type_name_reader.position
            type_name = type_name_reader.unpack_string(encoding="ascii")
            self.class_names[type_name_offset] = type_name
            self.class_hashes[type_name] = hsh

            # TODO: Hashes are checked in `TypeInfo` with everything else.

    def unpack_type_entries(
        self,
        type_section_reader: BinaryReader,
        entry_specs: list[dict[str, int]],
        section_end_offset: int,
    ) -> list[PackFileTypeEntry]:
        """Meow's "virtual fixups" are really just offsets to class names. I don't track them, because they only need
        to be reconstructed again on `pack()`.
        """
        type_entries = []
        for i, entry_spec in enumerate(entry_specs):
            class_name = self.class_names[entry_spec["type_name_offset"]]

            if i < len(entry_specs) - 1:
                data_size = entry_specs[i + 1]["relative_entry_offset"] - entry_spec["relative_entry_offset"]
            else:
                data_size = section_end_offset - entry_spec["relative_entry_offset"]

            type_section_reader.seek(entry_spec["relative_entry_offset"])
            type_entry = PackFileTypeEntry(class_name)
            type_entry.unpack(type_section_reader, data_size=data_size)
            type_entries.append(type_entry)

        return type_entries

    def unpack_item_entries(
        self,
        data_section_reader: BinaryReader,
        entry_specs: list[dict[str, int]],
        section_end_offset: int,
    ) -> list[PackFileItemEntry]:
        """Meow's "virtual fixups" are really just offsets to class names. I don't track them, because they only need
        to be reconstructed again on `pack()`.
        """
        data_entries = []
        for i, entry_spec in enumerate(entry_specs):
            type_name = self.class_names[entry_spec["type_name_offset"]]
            type_py_name = get_py_name(type_name)
            try:
                hk_type = getattr(self.hk_types_module, type_py_name)
            except AttributeError:
                # Missing type. Print `TypeInfo`.
                type_info = [t for t in self.hk_type_infos if t.name == type_name][0]
                print(type_info)
                raise


            if i < len(entry_specs) - 1:
                data_size = entry_specs[i + 1]["relative_entry_offset"] - entry_spec["relative_entry_offset"]
            else:
                data_size = section_end_offset - entry_spec["relative_entry_offset"]

            data_section_reader.seek(entry_spec["relative_entry_offset"])
            data_entry = PackFileItemEntry(hk_type)
            data_entry.unpack(data_section_reader, data_size=data_size)
            data_entries.append(data_entry)

        return data_entries

    def raw_repr(self):
        lines = ["Entries:"]
        for entry in self.items:
            lines.append(f"    Type: {entry.hk_type.__name__}")
            lines.append(
                f"        Location: ["
                f"{hex(entry.offset_in_section)} - {hex(entry.offset_in_section + entry.entry_byte_size)}"
                f"]"
            )
            lines.append(f"        Sub pointers ({len(entry.child_pointers)}):")
            for ref_source, ref_dest in entry.child_pointers.items():
                lines.append(f"            Local Offset: {ref_source} -> {ref_dest}")
            lines.append(f"        Entry pointers ({len(entry.entry_pointers)}):")
            for ref_source, (dest_entry, ref_dest) in entry.entry_pointers.items():
                lines.append(f"            Global Offset: {ref_source} -> {ref_dest} ({dest_entry.hk_type.__name__})")
            lines.append(f"        Raw data length: {len(entry.raw_data)}")
        return "\n".join(lines)


class TypeUnpacker:
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
        hk_types_module = None,
    ):
        self.type_entries = type_entries
        self.type_hashes = type_hashes
        self.pointer_size = pointer_size
        self.hk_types_module = hk_types_module

        self.enum_dicts = {}  # type: dict[int, TypeUnpacker.EnumValues]  # maps enum entry indices to value dict

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
        class_enums = {}  # type: dict[str, TypeUnpacker.EnumValues]
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
                    if _DEBUG_TYPE_PRINT:
                        print(f"Member \"{member_name}\"")
                    member_super_and_data_types = member["member_super_and_data_types"]
                    try:
                        member_super_type = PackMemberType.get_data_type(member_super_and_data_types)
                        member_data_type = PackMemberType.get_pointer_type(member_super_and_data_types)
                    except ValueError:
                        raise ValueError(
                            f"Member {member_name} of type {name} has unknown super/data type: "
                            f"{member_super_and_data_types:016b}"
                        )
                    if _DEBUG_TYPE_PRINT:
                        print(f"  {member_super_type.name} | {member_data_type.name}")

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
                    if _DEBUG_TYPE_PRINT:
                        print(f"  -> {type_py_name}")
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
        if _DEBUG_TYPE_PRINT:
            print(f"   Enum {name}:")
        with entry.reader.temp_offset(entry.child_pointers[enum_offset + self.pointer_size]):
            for _ in range(enum_type_struct["items_count"]):
                item_value = entry.reader.unpack_value("<I" if self.pointer_size == 4 else "<Q")
                item_name_offset = entry.child_pointers[entry.reader.position]
                item_name = entry.reader.unpack_string(offset=item_name_offset, encoding="utf-8")
                entry.reader.unpack_value("<I" if self.pointer_size == 4 else "<Q", asserted=0)
                if _DEBUG_TYPE_PRINT:
                    print(f"       {item_name} = {item_value}")
                items.append((item_name, item_value))

        return TypeUnpacker.EnumValues(name, items)


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
