from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *
from .hkcdStaticTreeTreehkcdStaticTreeDynamicStorage4 import hkcdStaticTreeTreehkcdStaticTreeDynamicStorage4
from .hkcdStaticMeshTreeBaseSectionSharedVertices import hkcdStaticMeshTreeBaseSectionSharedVertices
from .hkcdStaticMeshTreeBaseSectionPrimitives import hkcdStaticMeshTreeBaseSectionPrimitives
from .hkcdStaticMeshTreeBaseSectionDataRuns import hkcdStaticMeshTreeBaseSectionDataRuns


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkcdStaticMeshTreeBaseSection(hkcdStaticTreeTreehkcdStaticTreeDynamicStorage4):
    """
    public enum Flags
    {
        SF_REQUIRE_TREE = 1,
    }
    """
    alignment = 16
    byte_size = 96
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 4244753624

    local_members = (
        Member(48, "codecParms_0", _float),
        Member(52, "codecParms_1", _float), 
        Member(56, "codecParms_2", _float), 
        Member(60, "codecParms_3", _float), 
        Member(64, "codecParms_4", _float), 
        Member(68, "codecParms_5", _float), 
        Member(72, "firstPackedVertex", hkUint32), 
        Member(76, "sharedVertices", hkcdStaticMeshTreeBaseSectionSharedVertices), 
        Member(80, "primitives", hkcdStaticMeshTreeBaseSectionPrimitives),
        Member(84, "dataRuns", hkcdStaticMeshTreeBaseSectionDataRuns),
        Member(88, "numPackedVertices", hkUint8),
        Member(89, "numSharedIndices", hkUint8),
        Member(90, "leafIndex", hkUint16),
        Member(92, "page", hkUint8),
        Member(93, "flags", hkUint8),
        Member(94, "layerData", hkUint8),
        Member(95, "unusedData", hkUint8),
    )
    members = hkcdStaticTreeTreehkcdStaticTreeDynamicStorage4.members + local_members

    codecParms_0: float
    codecParms_1: float
    codecParms_2: float
    codecParms_3: float
    codecParms_4: float
    codecParms_5: float
    firstPackedVertex: int
    sharedVertices: hkcdStaticMeshTreeBaseSectionSharedVertices
    primitives: hkcdStaticMeshTreeBaseSectionPrimitives
    dataRuns: hkcdStaticMeshTreeBaseSectionDataRuns
    numPackedVertices: int
    numSharedIndices: int
    leafIndex: int
    page: int
    flags: int
    layerData: int
    unusedData: int
