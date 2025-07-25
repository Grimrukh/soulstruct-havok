from __future__ import annotations

from dataclasses import dataclass

from soulstruct.havok.enums import *
from ..core import *
from .hclOperator import hclOperator

from .hclSimulateOperatorConfig import hclSimulateOperatorConfig


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hclSimulateOperator(hclOperator):
    alignment = 8
    byte_size = 96
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __hsh = 1931677792
    __version = 4

    local_members = (
        Member(72, "simClothIndex", hkUint32),
        Member(80, "simulateOpConfigs", hkArray(hclSimulateOperatorConfig, hsh=137221530)),
    )
    members = hclOperator.members + local_members

    simClothIndex: int
    simulateOpConfigs: list[hclSimulateOperatorConfig]
