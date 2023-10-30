from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *

from .hknpBodyQuality import hknpBodyQuality


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
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

    qualityModifiedSignal: None = None
    qualities: tuple[hknpBodyQuality]
