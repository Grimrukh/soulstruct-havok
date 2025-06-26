from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *

from ..hkCompressedMassProperties import hkCompressedMassProperties


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hknpShapeMassProperties(hkReferencedObject):
    alignment = 8
    byte_size = 56
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 3077614392

    local_members = (
        Member(24, "compressedMassProperties", hkCompressedMassProperties),
    )
    members = hkReferencedObject.members + local_members

    compressedMassProperties: hkCompressedMassProperties
