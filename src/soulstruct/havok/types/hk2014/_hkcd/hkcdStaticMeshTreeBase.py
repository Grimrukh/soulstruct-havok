from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *

from ..core import *
from .hkcdStaticTreeTreehkcdStaticTreeDynamicStorage5 import hkcdStaticTreeTreehkcdStaticTreeDynamicStorage5
from .hkcdStaticMeshTreeBaseSection import hkcdStaticMeshTreeBaseSection
from .hkcdStaticMeshTreeBasePrimitive import hkcdStaticMeshTreeBasePrimitive


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkcdStaticMeshTreeBase(hkcdStaticTreeTreehkcdStaticTreeDynamicStorage5):
    """
    public enum CompressionMode
    {
        CM_GLOBAL = 0,
        CM_LOCAL_4 = 1,
        CM_LOCAL_2 = 2,
        CM_AUTO = 3,
    }
    """
    alignment = 16
    byte_size = 112
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 4169522384

    local_members = (
        Member(48, "numPrimitiveKeys", hkInt32),
        Member(52, "bitsPerKey", hkInt32),
        Member(56, "maxKeyValue", hkUint32),
        # Four 16-aligning bytes here.
        Member(64, "sections", hkArray(hkcdStaticMeshTreeBaseSection)),
        Member(80, "primitives", hkArray(hkcdStaticMeshTreeBasePrimitive)),
        Member(96, "sharedVerticesIndex", hkArray(hkUint16)),
    )
    members = hkcdStaticTreeTreehkcdStaticTreeDynamicStorage5.members + local_members

    numPrimitiveKeys: int
    bitsPerKey: int
    maxKeyValue: int
    sections: list[hkcdStaticMeshTreeBaseSection]
    primitives: list[hkcdStaticMeshTreeBasePrimitive]
    sharedVerticesIndex: list[int]
