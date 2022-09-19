from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *

from .hkaSkeleton import hkaSkeleton
from .hkaAnimation import hkaAnimation
from .hkaAnimationBinding import hkaAnimationBinding
from .hkaBoneAttachment import hkaBoneAttachment
from .hkaMeshBinding import hkaMeshBinding


class hkaAnimationContainer(hkReferencedObject):
    alignment = 8
    byte_size = 104
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 2343308884
    __version = 1

    local_members = (
        Member(24, "skeletons", hkArray(hkRefPtr(hkaSkeleton, hsh=3659816570), hsh=1926479907)),
        Member(40, "animations", hkArray(hkRefPtr(hkaAnimation))),
        Member(56, "bindings", hkArray(hkRefPtr(hkaAnimationBinding))),
        Member(72, "attachments", hkArray(hkRefPtr(hkaBoneAttachment))),
        Member(88, "skins", hkArray(hkRefPtr(hkaMeshBinding))),
    )
    members = hkReferencedObject.members + local_members

    skeletons: list[hkaSkeleton]
    animations: list[hkaAnimation]
    bindings: list[hkaAnimationBinding]
    attachments: list[hkaBoneAttachment]
    skins: list[hkaMeshBinding]
