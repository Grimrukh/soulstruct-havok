from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from .core import *


from .hkcdStaticTreeAabbTreeBase import hkcdStaticTreeAabbTreeBase
from .hkcdCompressedAabbCodecsAabb6BytesCodec import hkcdCompressedAabbCodecsAabb6BytesCodec
from .hkAabb import hkAabb


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkcdStaticTreeAabbTree(hkcdStaticTreeAabbTreeBase):
    alignment = 16
    byte_size = 48
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hkcdStaticTree::AabbTree"

    local_members = (
        Member(0, "nodes", hkArray(hkcdCompressedAabbCodecsAabb6BytesCodec, hsh=1776713336)),
        Member(16, "domain", hkAabb),
    )
    members = hkcdStaticTreeAabbTreeBase.members + local_members

    nodes: list[hkcdCompressedAabbCodecsAabb6BytesCodec]
    domain: hkAabb

    __templates = (
        TemplateType("tNODE", _type=hkcdCompressedAabbCodecsAabb6BytesCodec),
    )
