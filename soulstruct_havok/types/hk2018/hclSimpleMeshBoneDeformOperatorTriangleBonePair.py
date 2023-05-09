from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .core import *


@dataclass(slots=True, eq=False, repr=False)
class hclSimpleMeshBoneDeformOperatorTriangleBonePair(hk):
    alignment = 2
    byte_size = 4
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 2878957036
    __real_name = "hclSimpleMeshBoneDeformOperator::TriangleBonePair"

    local_members = (
        Member(0, "boneOffset", hkUint16),
        Member(2, "triangleOffset", hkUint16),
    )
    members = local_members

    boneOffset: int
    triangleOffset: int
