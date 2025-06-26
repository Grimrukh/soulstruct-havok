from __future__ import annotations

import typing as tp
from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .hkcdStaticMeshTreeBase import hkcdStaticMeshTreeBase

if tp.TYPE_CHECKING:
    from .._hknp.hknpCompressedMeshShapeTreeDataRun import hknpCompressedMeshShapeTreeDataRun


def deferred_hknpCompressedMeshShapeTreeDataRunData():
    # NOTE: The back-and-forth usage between `hkcd` and `hknp` with these ludicrous (REAL) class names is silly, Havok.
    # I've elected to make `hkcd` NOT dependent on `hknp` at all.
    from .._hknp.hknpCompressedMeshShapeTreeDataRunData import hknpCompressedMeshShapeTreeDataRunData
    return hknpCompressedMeshShapeTreeDataRunData


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkcdStaticMeshTreehkcdStaticMeshTreeCommonConfigunsignedintunsignedlonglong1121hknpCompressedMeshShapeTreeDataRun(hkcdStaticMeshTreeBase):
    """Yes, this is the REAL HAVOK CLASS NAME. The nadir of Havok.

    public enum TriangleMaterial
    {
        TM_SET_FROM_TRIANGLE_DATA_TYPE = 0,
        TM_SET_FROM_PRIMITIVE_KEY = 1,
    }
    """
    alignment = 16
    byte_size = 160
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 497573378

    local_members = (
        Member(112, "packedVertices", hkArray(hkUint32)),
        Member(128, "sharedVertices", hkArray(hkUint64)),
        Member(
            144,
            "primitiveDataRuns",
            hkArray(DefType("hknpCompressedMeshShapeTreeDataRunData", deferred_hknpCompressedMeshShapeTreeDataRunData)),
        ),
    )
    members = hkcdStaticMeshTreeBase.members + local_members

    packedVertices: list[int]
    sharedVertices: list[int]
    primitiveDataRuns: list[hknpCompressedMeshShapeTreeDataRun]
