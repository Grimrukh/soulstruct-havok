from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *

from .hkcdStaticTreeAabbTree import hkcdStaticTreeAabbTree


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkcdStaticTreeAabb6BytesTree(hkcdStaticTreeAabbTree):
    """Havok alias."""
    __tag_format_flags = 4
    __real_name = "hkcdStaticTree::Aabb6BytesTree"
    __version = 0
    local_members = ()
