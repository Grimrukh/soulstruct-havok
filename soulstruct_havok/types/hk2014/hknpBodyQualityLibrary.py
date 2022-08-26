from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *
from .hknpBodyQuality import hknpBodyQuality


class hknpBodyQualityLibrary(hkReferencedObject):
    alignment = 16
    byte_size = 544
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(16, "qualityModifiedSignal", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(32, "qualities", hkStruct(hknpBodyQuality, 32)),
    )
    members = hkReferencedObject.members + local_members

    qualityModifiedSignal: None
    qualities: tuple[hknpBodyQuality, ...]
