from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hclSimClothDataTransferMotionData(hk):
    alignment = 4
    byte_size = 48
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __real_name = "hclSimClothData::TransferMotionData"

    local_members = (
        Member(0, "transformSetIndex", hkUint32),
        Member(4, "transformIndex", hkUint32),
        Member(8, "transferTranslationMotion", hkBool),
        Member(12, "minTranslationSpeed", hkReal),
        Member(16, "maxTranslationSpeed", hkReal),
        Member(20, "minTranslationBlend", hkReal),
        Member(24, "maxTranslationBlend", hkReal),
        Member(28, "transferRotationMotion", hkBool),
        Member(32, "minRotationSpeed", hkReal),
        Member(36, "maxRotationSpeed", hkReal),
        Member(40, "minRotationBlend", hkReal),
        Member(44, "maxRotationBlend", hkReal),
    )
    members = local_members

    transformSetIndex: int
    transformIndex: int
    transferTranslationMotion: bool
    minTranslationSpeed: float
    maxTranslationSpeed: float
    minTranslationBlend: float
    maxTranslationBlend: float
    transferRotationMotion: bool
    minRotationSpeed: float
    maxRotationSpeed: float
    minRotationBlend: float
    maxRotationBlend: float
