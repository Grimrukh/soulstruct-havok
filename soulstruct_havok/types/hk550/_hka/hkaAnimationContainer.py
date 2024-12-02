from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *
from .hkaSkeleton import hkaSkeleton
from .hkaSkeletalAnimation import hkaSkeletalAnimation
from .hkaAnimationBinding import hkaAnimationBinding
from .hkaBoneAttachment import hkaBoneAttachment
from .hkaMeshBinding import hkaMeshBinding


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkaAnimationContainer(hk):
    alignment = 8
    byte_size = 40
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 4099301997

    local_members = (
        Member(0, "skeletons", SimpleArray(Ptr(hkaSkeleton))),
        Member(8, "animations", SimpleArray(Ptr(hkaSkeletalAnimation))),
        Member(16, "bindings", SimpleArray(Ptr(hkaAnimationBinding))),
        Member(24, "attachments", SimpleArray(Ptr(hkaBoneAttachment))),
        Member(32, "skins", SimpleArray(Ptr(hkaMeshBinding))),
    )
    members = local_members

    skeletons: list[hkaSkeleton]
    animations: list[hkaSkeletalAnimation]
    bindings: list[hkaAnimationBinding]
    attachments: list[hkaBoneAttachment]
    skins: list[hkaMeshBinding]
