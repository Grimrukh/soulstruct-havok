from __future__ import annotations

from soulstruct_havok.enums import *
from .core import *


from .hknpMotionProperties import hknpMotionProperties


@dataclass(slots=True, eq=False, repr=False)
class hknpMotionPropertiesLibrary(hkReferencedObject):
    alignment = 8
    byte_size = 72
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(24, "entryAddedSignal", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(32, "entryModifiedSignal", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(40, "entryRemovedSignal", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(48, "entries", hkFreeListArray(hknpMotionProperties, hkInt32), MemberFlags.Protected),
    )
    members = hkReferencedObject.members + local_members

    entryAddedSignal: hkReflectDetailOpaque
    entryModifiedSignal: hkReflectDetailOpaque
    entryRemovedSignal: hkReflectDetailOpaque
    entries: list[hknpMotionProperties]
