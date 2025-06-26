from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .._hkcd.hkcdStaticMesh__hknpCompressedMeshShapeTreeDataRun import (
    hkcdStaticMeshTreehkcdStaticMeshTreeCommonConfigunsignedintunsignedlonglong1121hknpCompressedMeshShapeTreeDataRun
)


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hknpCompressedMeshShapeTree(hkcdStaticMeshTreehkcdStaticMeshTreeCommonConfigunsignedintunsignedlonglong1121hknpCompressedMeshShapeTreeDataRun):
    alignment = 16
    byte_size = 160
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 3976603225

    local_members = ()
