from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *
from .hkaSkeleton import hkaSkeleton
from .hkaAnimation import hkaAnimation
from .hkaAnimationBinding import hkaAnimationBinding
from .hkaBoneAttachment import hkaBoneAttachment
from .hkaMeshBinding import hkaMeshBinding


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaAnimationContainer(hkReferencedObject):
    alignment = 16
    byte_size = 68
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 2378302259

    local_members = (
        Member(8, "skeletons", hkArray(Ptr(hkaSkeleton))),
        Member(20, "animations", hkArray(Ptr(hkaAnimation))),
        Member(32, "bindings", hkArray(Ptr(hkaAnimationBinding))),
        Member(44, "attachments", hkArray(Ptr(hkaBoneAttachment))),
        Member(56, "skins", hkArray(Ptr(hkaMeshBinding))),
    )
    members = hkReferencedObject.members + local_members

    skeletons: list[hkaSkeleton]
    animations: list[hkaAnimation]
    bindings: list[hkaAnimationBinding]
    attachments: list[hkaBoneAttachment]
    skins: list[hkaMeshBinding]
