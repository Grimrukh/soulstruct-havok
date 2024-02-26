"""Pointer that always points to a `hkbBehaviorGraph`, which is a higher class and may cause circularity."""
from __future__ import annotations

import typing as tp
from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *

if tp.TYPE_CHECKING:
    from .hkbBehaviorGraph import hkbBehaviorGraph


def deferred_hkbBehaviorGraph():
    from .hkbBehaviorGraph import hkbBehaviorGraph
    return hkbBehaviorGraph


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkAssetRefPtr(hk):
    alignment = 8
    byte_size = 8
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "ptr", Ptr(DefType("hkbBehaviorGraph", deferred_hkbBehaviorGraph)), MemberFlags.Private),
    )
    members = local_members

    ptr: "hkbBehaviorGraph"

    __templates = (
        TemplateType("tTYPE", _type=DefType("hkbBehaviorGraph", deferred_hkbBehaviorGraph)),
    )
