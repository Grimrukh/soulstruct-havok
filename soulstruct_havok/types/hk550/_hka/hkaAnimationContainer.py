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
class hkaAnimationContainer(hkReferencedObject):
    alignment = 16
    byte_size = 48
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 4099301997

    # NOTE: Class reflection isn't avaiable in the SDK, but the order of members defined in `hkaAnimationContainer.h` is
    # clearly wrong when looking at Demon's Souls files. `animations` and `bindings` are first, and I'm assuming that
    # `skeletons`, `attachments`, and `skins` come after that (can't confirm without a file that has any). Also note
    # that pre-2010 Havok uses `num...` fields and pointers-to-pointers rather than `hkArray` for some reason. Here,
    # these pointer/length member pairs are represented by a class called `SimpleArray`.
    local_members = (
        Member(8, "animations", SimpleArray(Ptr(hkaSkeletalAnimation))),
        Member(16, "bindings", SimpleArray(Ptr(hkaAnimationBinding))),
        # NOTE: Order of these three members is unconfirmed.
        Member(24, "skeletons", SimpleArray(Ptr(hkaSkeleton))),
        Member(32, "attachments", SimpleArray(Ptr(hkaBoneAttachment))),
        Member(40, "skins", SimpleArray(Ptr(hkaMeshBinding))),
    )
    members = hkReferencedObject.members + local_members

    skeletons: list[hkaSkeleton]
    animations: list[hkaSkeletalAnimation]
    bindings: list[hkaAnimationBinding]
    attachments: list[hkaBoneAttachment]
    skins: list[hkaMeshBinding]
