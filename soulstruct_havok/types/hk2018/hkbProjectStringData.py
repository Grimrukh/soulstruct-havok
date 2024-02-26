from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkbProjectStringData(hkReferencedObject):
    alignment = 8
    byte_size = 120
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 1263381213
    __version = 3

    local_members = (
        Member(24, "behaviorFilenames", hkArray(hkStringPtr, hsh=271207693)),
        Member(40, "characterFilenames", hkArray(hkStringPtr, hsh=271207693)),
        Member(56, "eventNames", hkArray(hkStringPtr, hsh=271207693)),
        Member(72, "animationPath", hkStringPtr),
        Member(80, "behaviorPath", hkStringPtr),
        Member(88, "characterPath", hkStringPtr),
        Member(96, "scriptsPath", hkStringPtr),
        Member(104, "fullPathToSource", hkStringPtr),
        Member(112, "rootPath", hkStringPtr, MemberFlags.NotSerializable),
    )
    members = hkReferencedObject.members + local_members

    behaviorFilenames: list[hkStringPtr]
    characterFilenames: list[hkStringPtr]
    eventNames: list[hkStringPtr]
    animationPath: hkStringPtr
    behaviorPath: hkStringPtr
    characterPath: hkStringPtr
    scriptsPath: hkStringPtr
    fullPathToSource: hkStringPtr
    rootPath: hkStringPtr
