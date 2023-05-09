from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *
from .hkaSkeleton import hkaSkeleton
from .hkaAnimation import hkaAnimation
from .hkaAnimationBinding import hkaAnimationBinding
from .hkaBoneAttachment import hkaBoneAttachment
from .hkaMeshBinding import hkaMeshBinding


@dataclass(slots=True, eq=False, repr=False)
class hkaAnimationContainer(hkReferencedObject):
    alignment = 16
    byte_size = 96
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 646291276
    __version = 1

    local_members = (
        Member(16, "skeletons", hkArray(Ptr(hkaSkeleton))),
        Member(32, "animations", hkArray(Ptr(hkaAnimation))),
        Member(48, "bindings", hkArray(Ptr(hkaAnimationBinding))),
        Member(64, "attachments", hkArray(Ptr(hkaBoneAttachment))),
        Member(80, "skins", hkArray(Ptr(hkaMeshBinding))),
    )
    members = hkReferencedObject.members + local_members

    skeletons: list[hkaSkeleton]
    animations: list[hkaAnimation]
    bindings: list[hkaAnimationBinding]
    attachments: list[hkaBoneAttachment]
    skins: list[hkaMeshBinding]
