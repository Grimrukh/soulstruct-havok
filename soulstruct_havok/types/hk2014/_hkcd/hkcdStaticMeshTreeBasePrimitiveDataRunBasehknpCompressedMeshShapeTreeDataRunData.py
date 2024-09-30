from __future__ import annotations

import typing as tp
from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *

if tp.TYPE_CHECKING:
    from .._hknp.hknpCompressedMeshShapeTreeDataRunData import hknpCompressedMeshShapeTreeDataRunData


def deferred_hknpCompressedMeshShapeTreeDataRunData():
    # NOTE: The back-and-forth usage between `hkcd` and `hknp` with these ludicrous (REAL) class names is silly, Havok.
    # I've elected to make `hkcd` NOT dependent on `hknp` at all.
    from .._hknp.hknpCompressedMeshShapeTreeDataRunData import hknpCompressedMeshShapeTreeDataRunData
    return hknpCompressedMeshShapeTreeDataRunData


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkcdStaticMeshTreeBasePrimitiveDataRunBasehknpCompressedMeshShapeTreeDataRunData(hk):
    alignment = 4
    byte_size = 4
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 2911068802

    local_members = (
        Member(
            0,
            "value",
            DefType("hknpCompressedMeshShapeTreeDataRunData", deferred_hknpCompressedMeshShapeTreeDataRunData),
        ),
        Member(2, "index", hkUint8),
        Member(3, "count", hkUint8),
    )
    members = local_members

    value: hknpCompressedMeshShapeTreeDataRunData
    index: int
    count: int
