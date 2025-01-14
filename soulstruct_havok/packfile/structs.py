from __future__ import annotations

__all__ = [
    "PackItemCreationQueues",
    "PackFileTypeItem",
    "PackFileDataItem",
    "PackFileHeader",
    "PackFileHeaderExtension",
    "PackFileSectionHeader",
    "PackFileVersion",
    "PackfileHeaderInfo",
    "ChildPointerStruct",
    "ItemPointerStruct",
    "ItemSpecStruct",
    "TYPE_NAME_HASHES",
]

import abc
import typing as tp
from collections import deque
from dataclasses import dataclass, field
from enum import IntEnum

from soulstruct_havok.enums import PyHavokModule

from soulstruct.utilities.binary import *
from soulstruct.utilities.inspection import get_hex_repr

if tp.TYPE_CHECKING:
    import numpy as np
    from soulstruct_havok.types.hk import hk
    from soulstruct_havok.types.base import hkArray_, Ptr_


@dataclass(slots=True)
class PackItemCreationQueues:
    # Pointers to arrays or strings inside the same item. These functions don't return new items.
    child_pointers: deque[tp.Callable[[PackItemCreationQueues], None]] = field(default_factory=deque)
    # Pointers to other items in the HKX (always actual `Ptr` types). These functions create and return items.
    item_pointers: deque[tp.Callable[[PackItemCreationQueues], PackFileDataItem]] = field(default_factory=deque)


@dataclass(slots=True)
class PackFileBaseItem(abc.ABC):
    """Base class for 'Type' and 'Item' entries in a PackFile section."""

    local_data_offset: int = -1
    item_byte_size: int = -1
    raw_data: bytes = b""
    byte_order: ByteOrder = ByteOrder.LittleEndian
    long_varints: bool = False

    # Maps source offsets to dest offsets inside same entry (arrays and strings).
    all_child_pointers: dict[int, int] = field(default_factory=dict)
    # Maps source offsets to other entries from same section (pointers).
    all_item_pointers: dict[int, tuple[PackFileBaseItem, int]] = field(default_factory=dict)

    reader: BinaryReader | None = None
    writer: BinaryWriter | None = None

    def unpack(self, section_reader: BinaryReader, data_size: int, byte_order: ByteOrder, long_varints: bool):
        """`section_reader` should be local for this section, NOT the whole HKX file."""
        self.local_data_offset = section_reader.position  # offset inside data section
        self.item_byte_size = data_size
        self.raw_data = section_reader.read(data_size)  # parsed later
        self.byte_order = byte_order
        self.long_varints = long_varints

    def get_offset_in_item(self, offset: int) -> int:
        """Returns given offset relative to the start of this item, if it is inside this item.

        Otherwise, returns -1.
        """
        if self.local_data_offset <= offset < self.local_data_offset + self.item_byte_size:
            return offset - self.local_data_offset
        return -1

    def start_reader(self):
        """Create raw data reader. Raises `ValueError` if the reader was already created."""
        if self.reader is not None:
            raise ValueError(f"`{self.__class__.__name__}` reader was already created.")
        self.reader = BinaryReader(self.raw_data, byte_order=self.byte_order, long_varints=self.long_varints)

    def start_writer(self):
        if self.writer is not None:
            raise ValueError(f"`{self.__class__.__name__}` writer was already created.")
        self.writer = BinaryWriter(byte_order=self.byte_order, long_varints=self.long_varints)

    @property
    def hex(self):
        if self.writer:
            return self.writer.position_hex
        if self.reader:
            return self.reader.position_hex
        return "XX"

    @property
    def all_child_pointers_hex(self) -> dict[str, str]:
        return {hex(k): hex(v) for k, v in self.all_child_pointers.items()}

    @property
    def all_item_pointers_hex(self) -> dict[str, tuple[PackFileBaseItem, int]]:
        return {hex(k): v for k, v in self.all_item_pointers.items()}


@dataclass(slots=True)
class PackFileTypeItem(PackFileBaseItem):

    class TYPE_STRUCT_32(BinaryStruct):
        type_name_pointer: uint = field(init=False, **Binary(asserted=0))  # child pointer
        parent_type_pointer: uint = field(init=False, **Binary(asserted=0))  # item pointer
        byte_size: uint
        interface_count: uint
        enums_pointer: uint = field(init=False, **Binary(asserted=0))  # child pointer (NOT an item pointer to enum!)
        enums_count: uint
        member_pointer: uint = field(init=False, **Binary(asserted=0))  # child pointer
        member_count: uint
        defaults: uint  # child pointer
        flags: uint  # always zero so far in packfiles (could be padding!)
        version: uint  # always zero so far in packfiles (could be padding!)

    class TYPE_STRUCT_64(BinaryStruct):
        """NOTE: Differences are not entirely just `varint` size."""
        type_name_pointer: ulong = field(init=False, **Binary(asserted=0))  # child pointer
        parent_type_pointer: ulong = field(init=False, **Binary(asserted=0))  # item pointer
        byte_size: uint
        interface_count: uint
        enums_pointer: ulong = field(init=False, **Binary(asserted=0))  # child pointer (NOT an item pointer to enum!)
        enums_count: uint
        _pad1: bytes = field(init=False, **BinaryPad(4))  # TODO: padding could be earlier (but after byte size)
        member_pointer: ulong = field(init=False, **Binary(asserted=0))  # child pointer
        member_count: uint
        defaults: uint  # child pointer
        flags: uint  # always zero so far in packfiles (could be padding!)
        _pad2: bytes = field(init=False, **BinaryPad(16))  # TODO: padding could be earlier (but after member count)
        version: uint  # always zero in 2010

    class ENUM_TYPE_STRUCT(BinaryStruct):
        name_pointer: varuint = field(init=False, **Binary(asserted=0))  # child pointer
        items_pointer: varuint = field(init=False, **Binary(asserted=0))  # child pointer
        items_count: uint
        attributes_pointer: varuint
        flags: uint
        # 12 bytes of padding here in actual type entries (16 align), but no padding in "embedded" enums inside types.

    class MEMBER_TYPE_STRUCT(BinaryStruct):
        name_pointer: varuint = field(init=False, **Binary(asserted=0))  # child pointer
        type_pointer: varuint = field(init=False, **Binary(asserted=0))  # item pointer
        enum_pointer: varuint = field(init=False, **Binary(asserted=0))  # item pointer
        member_type: byte
        member_subtype: byte
        c_array_size: ushort  # size of tuple T[N]; usually zero
        flags: ushort
        offset: ushort
        attributes_pointer: varuint  # never observed; assuming this never occurs

    GENERIC_TYPE_NAMES = ["hkArray", "hkEnum", "hkRefPtr", "hkViewPtr", "T*", "T[N]"]

    class_name: str = ""
    # Type override.
    all_item_pointers: dict[int, tuple[PackFileTypeItem, int]] = field(default_factory=dict)

    def get_type_name(self) -> str | None:
        """Quickly look up type name from raw data. Returns `None` if `child_pointers` is undefined/empty."""
        if not self.all_child_pointers:
            return None
        return BinaryReader(self.raw_data).unpack_string(offset=self.all_child_pointers[0], encoding="utf-8")

    def get_byte_size(self) -> int:
        return BinaryReader(self.raw_data).unpack_value("I", offset=8)

    def get_referenced_type_item(self, offset: int) -> PackFileTypeItem | None:
        """Look for `self.item_pointers[offset]` and recover the pointed `PackFileTypeItem`."""
        if offset in self.all_item_pointers:
            type_item, zero = self.all_item_pointers[offset]
            if zero != 0:
                raise AssertionError(f"Found type item pointer placeholder other than zero: {zero}")
            return type_item
        # Member is not a class or pointer.
        return None

    def __repr__(self):
        return f"PackFileTypeItem({self.get_type_name()})"


@dataclass(slots=True, kw_only=True)
class PackFileDataItem(PackFileBaseItem):

    all_item_pointers: dict[int, tuple[PackFileDataItem, int]] = field(default_factory=dict)  # type override

    hk_type: tp.Type[hk | hkArray_ | Ptr_] | None = None
    value: None | hk | bool | int | float | list | tuple | np.ndarray = None
    # Packer-managed lists of functions that fill in short array jumps later (written after members but before arrays).
    pending_rel_arrays: list[deque[tp.Callable]] = field(default_factory=list)

    remaining_child_pointers: dict[int, int] = field(default_factory=dict)
    remaining_item_pointers: dict[int, tuple[PackFileDataItem, int]] = field(default_factory=dict)

    def get_type_name(self):
        """Get (real) Havok class name for packfile class name section."""
        if self.hk_type.__name__ == "hkRootLevelContainer":
            return "hkRootLevelContainer"
        # Otherwise, item type should be a pointer type.
        try:
            return type(self.value).get_real_name()
        except AttributeError:
            # Value has not been assigned. We use the specified type (could be a parent of assigned value).
            return self.hk_type.__name__

    def prepare_pointers(self):
        self.remaining_child_pointers = self.all_child_pointers.copy()
        self.remaining_item_pointers = self.all_item_pointers.copy()

    def print_item_dump(self):
        print(f"Item type: {self.hk_type.__name__}")
        print(f"Item child pointers: {self.all_child_pointers_hex}")
        print(f"Item item pointers: {self.all_item_pointers_hex}")
        if len(self.raw_data) < 1000:
            print(f"Item raw data:\n{get_hex_repr(self.raw_data)}")
        else:
            print(f"Item raw data (first 1000 bytes):\n{get_hex_repr(self.raw_data[:1000])}")

    def __repr__(self):
        return f"PackFileDataItem({self.hk_type.__name__ if self.hk_type else None})"


class PackFileVersion(IntEnum):
    Version0x05 = 0x05  # Demon's Souls
    Version0x08 = 0x08  # DS1:PTDE
    Version0x09 = 0x09  # DS1:PTDE (rare)
    Version0x0B = 0x0B  # Bloodborne, DS3, Sekiro

    @property
    def has_header_extension(self):
        return self == self.Version0x0B


class PackFileHeader(BinaryStruct):
    """Packfile header structure.

    Notes on `reuse_padding_optimization` from Havok 5.5.0:

        Determines whether members of subclasses appear after alignment padding. Say we have two structs:

        struct A { hkVector4 x; int i; };
        struct B : public A { int j; };

        All compilers have sizeof(A) == 2 * sizeof(hkVector4) because of the alignment padding (the alignment of the
        struct is equal to the alignment of its largest member). Some compilers simply append members of subclasses to
        the base class, i.e. so that `offsetof(B, j) == sizeof(A)` (reuse_padding_optimization == 0). Others can reuse
        the padding for derived classes so that `sizeof(B) == sizeof(A)` and `offsetof(B, j) == offsetof(B, i) +
        sizeof(int)` (reuse_padding_optimization == 1).

        Put another way: if `reuse_padding_optimization == 0`, alignment occurs BETWEEN the members of each class in
        a hierarchy of `hk` classes. If `reuse_padding_optimization == 1`, alignment only occurs after writing the
        complete bottom-level subclass.

    Notes on `empty_base_class_optimization` from Havok 5.5.0:

        Determines whether empty base classes are optimized out. Say we have two structs:

        struct A {};
        struct B : public A { int x; };

        All compilers have `sizeof(A) > 0`. Some compilers reuse the padding for derived class members such that
        `offsetof(B, x) == 0` (empty_base_class_optimization == 1).

        Always 1 for all FromSoft games observed so far. Note that `hkBaseObject`, despite having no members, always
        contains a null pointer (size 4 or 8) in HKX files for vtable storage.
    """

    magic0: uint = field(init=False, **Binary(asserted=0x57E0E057))
    magic1: uint = field(init=False, **Binary(asserted=0x10C0C010))
    user_tag: int = field(init=False, **Binary(asserted=0))  # 0 in all FromSoft games
    version: PackFileVersion = field(**Binary(int))

    # Four `LayoutRules` bytes:
    pointer_size: byte = field(**Binary(asserted=[4, 8]))
    is_little_endian: bool  # False for Demon's Souls only (not Bloodborne I think)
    reuse_padding_optimization: byte = field(**Binary(asserted=[0, 1]))  # 0 or 1 (1 in Demon's Souls, Bloodborne)
    empty_base_class_optimization: byte = field(init=False, **Binary(asserted=1))  # 1 in all FromSoft games

    section_count: int = field(init=False, **Binary(asserted=3))  # sections: classnames, types, data
    data_section_index: int = field(**Binary(asserted=[0, 1, 2]))  # usually 2
    data_section_base_offset: int = field(init=False, **Binary(asserted=0))  # just the start of data section
    classnames_section_index: int = field(**Binary(asserted=[0, 1, 2]))  # usually 0
    classnames_section_root_offset: int  # relative offset of string 'hkRootLevelContainer' in classnames (often 0x4b)
    contents_version_string: str = field(**BinaryString(14, encoding="ascii"))  # e.g. "hk_2010.2.0-r1"
    _pad1: bytes = field(init=False, **BinaryPad(1))
    _minus_one: byte = field(init=False, **Binary(asserted=0xFF))
    flags: int  # usually -1 or 0

    def get_section_order(self) -> dict[str, int]:
        """Infer section order from `data_section_index` and `classnames_section_index`.

        Almost always `{classnames: 0, types: 1, data: 2}`.
        """
        return {
            "classnames": self.classnames_section_index,
            "types": next(iter({0, 1, 2} - {self.classnames_section_index, self.data_section_index})),
            "data": self.data_section_index,
        }


class PackFileHeaderExtension(BinaryStruct):
    unk_x3c: short
    section_offset: short
    unk_x40: uint
    unk_x44: uint
    unk_x48: uint
    unk_x4c: uint


class PackFileSectionHeader(BinaryStruct):
    """Packfile section header structure."""
    section_tag: bytes = field(**BinaryString(19))  # e.g. b"__classnames__" (type section)
    minus_one: byte = field(init=False, **Binary(asserted=0xFF))
    absolute_data_start: uint
    child_pointers_offset: uint  # "local fixups"
    item_pointers_offset: uint  # "global fixups"
    item_specs_offset: uint  # "virtual fixups"
    exports_offset: uint
    imports_offset: uint
    end_offset: uint
    
    @classmethod
    def get_reserved_header(cls, section_tag: bytes):
        """Return an instance of this class with all fields reserved except given `section_tag`."""
        return cls(
            section_tag=section_tag,
            absolute_data_start=RESERVED,
            child_pointers_offset=RESERVED,
            item_pointers_offset=RESERVED,
            item_specs_offset=RESERVED,
            exports_offset=RESERVED,
            imports_offset=RESERVED,
            end_offset=RESERVED,
        )

    def fill_type_name_or_type_section(self, writer: BinaryWriter, absolute_data_start: int, end_offset: int):
        writer.fill("absolute_data_start", absolute_data_start, obj=self)
        for field_name in (
            "child_pointers_offset",
            "item_pointers_offset",
            "item_specs_offset",
            "exports_offset",
            "imports_offset",
            "end_offset",
        ):
            writer.fill(field_name, end_offset, obj=self)


@dataclass(slots=True)
class PackfileHeaderInfo:
    """Minimal info needed to pack a packfile. Stored in `HKX` and must be passed to `PackFileUnpacker`."""
    header_version: PackFileVersion
    pointer_size: int
    is_little_endian: bool
    reuse_padding_optimization: int
    contents_version_string: str
    flags: int
    header_extension: None | PackFileHeaderExtension = None  # optional (only in version 0x0B: Bloodborne)

    @property
    def long_varints(self) -> bool:
        if self.pointer_size == 8:
            return True
        elif self.pointer_size == 4:
            return False
        else:
            raise ValueError(f"Invalid pointer size: {self.pointer_size}")


class ChildPointerStruct(BinaryStruct):
    source_offset: uint
    dest_offset: uint


class ItemPointerStruct(BinaryStruct):
    source_offset: uint
    dest_section_index: uint  # usually 2 (__data__)
    dest_offset: uint  # usually zero


class ItemSpecStruct(BinaryStruct):
    local_data_offset: uint  # relative offset into "__data__" section
    type_section_index: uint = field(init=False, **Binary(asserted=0))  # always references type section
    type_name_offset: uint  # offset into `section_index` above (always type section)


# Hashes for Havok types (typically generic types) that do not have a hash in the known database XML.
TYPE_NAME_HASHES = {
    # TODO: Most of these can go in their Python types.
    PyHavokModule.hk550: {
        "hkClass": 2384426808,  # TODO: 947330958 in animation HKX
        "hkClassMember": 1460610213,  # TODO: 2770603863 in animation HKX
        "hkClassEnum": 3473487498,  # TODO: 2318797263 in animation HKX
        "hkClassEnumItem": 1821011918,  # TODO: 3463416428 in animation HKX
        "hkpPhantom": 450759338,
        "hkAabb": 378246218,
        "hkpEntitySmallArraySerializeOverrideType": 3244565483,
        "hkpPhysicsData": 3831604418,
        "hkWorldMemoryAvailableWatchDog": 3036025613,
        "hkpPhysicsSystem": 4025505819,
        "hkSweptTransform": 1884769803,
        "hkpShapeContainer": 9072864,
        "hkpCollidable": 3282205016,
        "hkpBroadPhaseHandle": 3697870228,
        "hkpEntity": 931494394,
        "hkpShapeCollection": 1697782427,
        "hkpMaterial": 1688372484,
        "hkpExtendedMeshShapeTrianglesSubpart": 2620421427,
        "hkpKeyframedRigidMotion": 3207400075,
        "hkMoppBvTreeShapeBase": 248911681,
        "hkpMoppCode": 4166643314,
        "hkAabbUint32": 692521132,
        "hkpSphereRepShape": 3953650919,
        "hkpMoppBvTreeShape": 691845851,
        "hkpRigidBody": 1994269746,
        "hkpStorageExtendedMeshShapeMeshSubpartStorage": 1359687483,
        "hkpBvTreeShape": 3953650919,
        "hkpExtendedMeshShapeSubpart": 3342177404,
        "CustomMeshParameter": 3922497084,
        "hkpStorageExtendedMeshShape": 2661821634,
        "hkpExtendedMeshShape": 137956390,
        "hkpModifierConstraintAtom": 2335472315,
        "hkpSingleShapeContainer": 941468275,
        "hkReferencedObject": 319888443,
        "hkpCollisionFilter": 906204768,
        "hkpConstraintInstance": 1706373920,
        "hkpProperty": 3909673884,
        "hkRootLevelContainer": 1319344373,
        "hkpLinkedCollidable": 4041247054,
        "hkMultiThreadCheck": 545799196,
        "hkpWorldCinfo": 2507328831,
        "hkpMaxSizeMotion": 4176799915,
        "hkpPropertyValue": 2854574535,
        "hkpCdBody": 2284211689,
        "hkBaseObject": 9072864,
        "hkpShape": 2710594662,
        "hkpExtendedMeshShapeShapesSubpart": 2736185596,
        "hkpCollidableBoundingVolumeData": 659928215,
        "hkpConstraintData": 2265812929,
        "CustomParamStorageExtendedMeshShape": 1293002611,
        "hkpStorageExtendedMeshShapeShapeSubpartStorage": 3979946320,
        "hkpTypedBroadPhaseHandle": 461912485,
        "hkpMotion": 3384613396,
        "hkpWorldObject": 2683237968,
        "hkpAction": 1500419766,
        "hkpConvexListFilter": 2759118977,
        "hkpConvexShape": 2236610552,
        "hkRootLevelContainerNamedVariant": 2626239109,
        "hkpEntitySpuCollisionCallback": 92214401,
        "hkpMoppCodeCodeInfo": 146537944,
        "hkMotionState": 3833351686,
        "hkpConstraintAtom": 70097133,
    },
    PyHavokModule.hk2010: {
        "hkClass": 1968725750,
        "hkClassMember": 1551803586,
        "hkClassEnum": 2318797263,
        "hkClassEnumItem": 3463416428,
        "hkRootLevelContainer": 661831966,
        "hkaAnimationBinding": 1726663025,
        "hkaDefaultAnimatedReferenceFrame": 1837491269,
        "hkaSplineCompressedAnimation": 2033115323,
        "hkpPhysicsData": 3265552868,
        "hkpPhysicsSystem": 4285680663,
        "hkpRigidBody": 1979242501,
        "hkpMoppBvTreeShape": 2427624761,
        "hkpMoppCode": 2454464097,
        "CustomParamStorageExtendedMeshShape": 2191966266,
        "hkpStorageExtendedMeshShapeMeshSubpartStorage": 1521307110,
        "CustomMeshParameter": 1015991529,

    },
    PyHavokModule.hk2014: {
        "hkClass": 869540739,
        "hkClassMember": 2968495897,
        "hkClassEnum": 2318797263,
        "hkClassEnumItem": 3463416428,
    }
}
