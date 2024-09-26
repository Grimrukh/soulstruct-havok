from __future__ import annotations

from dataclasses import dataclass

import typing as tp

from soulstruct_havok.enums import *
from ..core import *

from .hkpConstraintAtom import hkpConstraintAtom

if tp.TYPE_CHECKING:
    from .hkpConstraintData import hkpConstraintData


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkpBridgeConstraintAtom(hkpConstraintAtom):
    alignment = 16
    byte_size = 32
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(8, "buildJacobianFunc", Ptr(hkReflectDetailOpaque), MemberFlags.NotSerializable),
        Member(16, "constraintData", hkViewPtr("hkpConstraintData", hsh=525862446)),
    )
    members = hkpConstraintAtom.members + local_members

    buildJacobianFunc: None = None
    constraintData: hkpConstraintData
