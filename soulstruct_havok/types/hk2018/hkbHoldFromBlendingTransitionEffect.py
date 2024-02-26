from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


from .hkbBlendingTransitionEffect import hkbBlendingTransitionEffect


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkbHoldFromBlendingTransitionEffect(hkbBlendingTransitionEffect):
    alignment = 16
    byte_size = 432
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 308731867

    local_members = (
        Member(
            352,
            "heldFromPose",
            Ptr(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Private,
        ),
        Member(360, "heldFromPoseSize", _int, MemberFlags.NotSerializable | MemberFlags.Private),
        Member(368, "heldWorldFromModel", hkQsTransform, MemberFlags.NotSerializable | MemberFlags.Private),
        Member(
            416,
            "heldFromSkeleton",
            Ptr(hkReflectDetailOpaque),
            MemberFlags.NotSerializable | MemberFlags.Private,
        ),
        Member(424, "additiveFlag", hkInt8, MemberFlags.NotSerializable | MemberFlags.Private),
    )
    members = hkbBlendingTransitionEffect.members + local_members

    heldFromPose: hkReflectDetailOpaque
    heldFromPoseSize: int
    heldWorldFromModel: hkQsTransform
    heldFromSkeleton: hkReflectDetailOpaque
    additiveFlag: int
