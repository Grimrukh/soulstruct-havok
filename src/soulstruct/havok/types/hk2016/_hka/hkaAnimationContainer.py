from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .hkaSkeleton import hkaSkeleton
from .hkaAnimation import hkaAnimation
from .hkaAnimationBinding import hkaAnimationBinding
from .hkaBoneAttachment import hkaBoneAttachment
from .hkaMeshBinding import hkaMeshBinding


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaAnimationContainer(hkReferencedObject):
    alignment = 8
    byte_size = 96
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 3294833177
    __version = 1

    local_members = (
        Member(16, "skeletons", hkArray(hkRefPtr(hkaSkeleton))),
        Member(32, "animations", hkArray(hkRefPtr(hkaAnimation, hsh=835592334), hsh=2995419249)),
        Member(48, "bindings", hkArray(hkRefPtr(hkaAnimationBinding, hsh=2009438005), hsh=2651098392)),
        Member(64, "attachments", hkArray(hkRefPtr(hkaBoneAttachment))),
        Member(80, "skins", hkArray(hkRefPtr(hkaMeshBinding))),
    )
    members = hkReferencedObject.members + local_members

    skeletons: list[hkaSkeleton]
    animations: list[hkaAnimation]
    bindings: list[hkaAnimationBinding]
    attachments: list[hkaBoneAttachment]
    skins: list[hkaMeshBinding]
