from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *


from .hknpBodyQuality import hknpBodyQuality


class hknpBodyQualityLibrary(hkReferencedObject):
    alignment = 16
    byte_size = 1568
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 1

    local_members = (
        Member(24, "qualityModifiedSignal", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(32, "qualities", hkGenericStruct(hknpBodyQuality, 32), MemberFlags.Protected),
    )
    members = hkReferencedObject.members + local_members

    qualityModifiedSignal: hkReflectDetailOpaque
    qualities: tuple[hknpBodyQuality]
