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

if tp.TYPE_CHECKING:
    import numpy as np
    from soulstruct_havok.types.hk import hk
    from soulstruct_havok.types.base import hkArray_, Ptr_


@dataclass(slots=True)
class PackItemCreationQueues:
    # Byte order to use when creating items.
    byte_order: ByteOrder
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
    child_pointers: dict[int, int] = field(default_factory=dict)
    # Maps source offsets to other entries from same section (pointers).
    item_pointers: dict[int, tuple[PackFileBaseItem, int]] = field(default_factory=dict)

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
        self.reader = BinaryReader(self.raw_data, default_byte_order=self.byte_order, long_varints=self.long_varints)

    def start_writer(self, byte_order: ByteOrder):
        if self.writer is not None:
            raise ValueError(f"`{self.__class__.__name__}` writer was already created.")
        self.writer = BinaryWriter(byte_order=byte_order, long_varints=self.long_varints)


@dataclass(slots=True)
class PackFileTypeItem(PackFileBaseItem):

    @dataclass(slots=True)
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

    @dataclass(slots=True)
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

    @dataclass(slots=True)
    class ENUM_TYPE_STRUCT(BinaryStruct):
        name_pointer: varuint = field(init=False, **Binary(asserted=0))  # child pointer
        items_pointer: varuint = field(init=False, **Binary(asserted=0))  # child pointer
        items_count: uint
        attributes_pointer: varuint
        flags: uint
        # 12 bytes of padding here in actual type entries (16 align), but no padding in "embedded" enums inside types.

    @dataclass(slots=True)
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
    item_pointers: dict[int, tuple[PackFileTypeItem, int]] = field(default_factory=dict)

    def get_type_name(self) -> str | None:
        """Quickly look up type name from raw data. Returns `None` if `child_pointers` is undefined/empty."""
        if not self.child_pointers:
            return None
        return BinaryReader(self.raw_data).unpack_string(self.child_pointers[0], encoding="utf-8")

    def get_byte_size(self) -> int:
        return BinaryReader(self.raw_data).unpack_value("I", offset=8)

    def get_referenced_type_item(self, offset: int) -> PackFileTypeItem | None:
        """Look for `self.item_pointers[offset]` and recover the pointed `PackFileTypeItem`."""
        if offset in self.item_pointers:
            type_item, zero = self.item_pointers[offset]
            if zero != 0:
                raise AssertionError(f"Found type item pointer placeholder other than zero: {zero}")
            return type_item
        # Member is not a class or pointer.
        return None

    def __repr__(self):
        return f"PackFileTypeItem({self.get_type_name()})"


@dataclass(slots=True, kw_only=True)
class PackFileDataItem(PackFileBaseItem):

    item_pointers: dict[int, tuple[PackFileDataItem, int]] = field(default_factory=dict)  # type override

    hk_type: tp.Type[hk | hkArray_ | Ptr_] | None = None
    value: None | hk | bool | int | float | list | tuple | np.ndarray = None
    # Packer-managed lists of functions that fill in short array jumps later (written after members but before arrays).
    pending_rel_arrays: list[deque[tp.Callable]] = field(default_factory=list)

    def get_class_name(self):
        """Get (real) Havok class name for packfile class name section."""
        if self.hk_type.__name__ == "hkRootLevelContainer":
            return "hkRootLevelContainer"
        # Otherwise, item type should be a pointer type.
        try:
            return type(self.value).get_real_name()
        except AttributeError:
            raise ValueError(
                f"Packfile item type is not `hkRootLevelContainer` or a pointer: {type(self.value).__name__}"
            )

    def __repr__(self):
        return f"PackFileDataItem({self.hk_type.__name__ if self.hk_type else None})"


class PackFileVersion(IntEnum):
    Version0x05 = 0x05
    Version0x08 = 0x08
    Version0x09 = 0x09
    Version0x0B = 0x0B

    @property
    def has_header_extension(self):
        return self == self.Version0x0B


@dataclass(slots=True)
class PackFileHeader(BinaryStruct):
    """Packfile header structure."""

    magic0: uint = field(init=False, **Binary(asserted=0x57E0E057))
    magic1: uint = field(init=False, **Binary(asserted=0x10C0C010))
    user_tag: int = field(init=False, **Binary(asserted=0))
    version: PackFileVersion = field(**Binary(int))  # 0x05 (Des), 0x08/0x09 (DS1PTDE), 0x0B (BB/DS3/SEK)
    pointer_size: byte  # 4 or 8
    is_little_endian: bool  # usually True (post DeS I assume)
    padding_option: byte  # 0 or 1 (1 in Bloodborne)
    base_type: byte = field(init=False, **Binary(asserted=1))
    section_count: int = field(init=False, **Binary(asserted=3))  # sections: classnames, types, data
    data_section_index: int = field(init=False, **Binary(asserted=2))  # always third section
    data_section_base_offset: int = field(init=False, **Binary(asserted=0))  # just the start of data section
    classnames_section_index: int = field(init=False, **Binary(asserted=0))  # always first section
    classnames_section_root_offset: int  # relative offset of string 'hkRootLevelContainer' in classnames (often 75)
    contents_version_string: bytes = field(**BinaryString(14))  # e.g. "hk_2010.2.0-r1"
    _pad1: bytes = field(init=False, **BinaryPad(1))
    _minus_one: byte = field(init=False, **Binary(asserted=0xFF))
    flags: int  # usually 0


@dataclass(slots=True)
class PackFileHeaderExtension(BinaryStruct):
    unk_x3C: short
    section_offset: short
    unk_x40: uint
    unk_x44: uint
    unk_x48: uint
    unk_x4C: uint


@dataclass(slots=True)
class PackFileSectionHeader(BinaryStruct):
    """Packfile section header structure."""
    section_tag: bytes = field(**BinaryString(19))  # e.g. b"__classnames__" (type section)
    minus_one: byte = field(init=False, **Binary(asserted=0xFF))
    absolute_data_start: uint
    child_pointers_offset: uint
    item_pointers_offset: uint
    item_specs_offset: uint
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
    padding_option: int
    contents_version_string: bytes
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


@dataclass(slots=True)
class ChildPointerStruct(BinaryStruct):
    source_offset: uint
    dest_offset: uint


@dataclass(slots=True)
class ItemPointerStruct(BinaryStruct):
    source_offset: uint
    dest_section_index: uint  # usually 2 (__data__)
    dest_offset: uint  # usually zero


@dataclass(slots=True)
class ItemSpecStruct(BinaryStruct):
    local_data_offset: uint  # relative offset into "__data__" section
    type_section_index: uint = field(init=False, **Binary(asserted=0))  # always references type section
    type_name_offset: uint  # offset into `section_index` above (always type section)


# Hashes for Havok types (typically generic types) that do not have a hash in the known database XML.
TYPE_NAME_HASHES = {
    # TODO: Most of these can go in their Python types.
    PyHavokModule.hk550: {
        "hkClass": 2384426808,
        "hkClassMember": 1460610213,
        "hkClassEnum": 3473487498,
        "hkClassEnumItem": 1821011918,
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
