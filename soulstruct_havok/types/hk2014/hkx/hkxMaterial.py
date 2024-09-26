from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *
from .hkxAttributeHolder import hkxAttributeHolder
from .hkxMaterialTextureStage import hkxMaterialTextureStage
from .hkxMaterialUVMappingAlgorithm import hkxMaterialUVMappingAlgorithm
from .hkxMaterialTransparency import hkxMaterialTransparency
from .hkxMaterialProperty import hkxMaterialProperty


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkxMaterial(hkxAttributeHolder):
    alignment = 16
    byte_size = 224
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __version = 5

    local_members = (
        Member(32, "name", hkStringPtr),
        Member(40, "stages", hkArray(hkxMaterialTextureStage)),
        Member(64, "diffuseColor", hkVector4),
        Member(80, "ambientColor", hkVector4),
        Member(96, "specularColor", hkVector4),
        Member(112, "emissiveColor", hkVector4),
        Member(128, "subMaterials", hkArray(Ptr(DefType("hkxMaterial", lambda: hkxMaterial)))),
        Member(144, "extraData", Ptr(hkReferencedObject)),
        Member(152, "uvMapScale", hkStruct(hkReal, 2)),
        Member(160, "uvMapOffset", hkStruct(hkReal, 2)),
        Member(168, "uvMapRotation", hkReal),
        Member(172, "uvMapAlgorithm", hkEnum(hkxMaterialUVMappingAlgorithm, hkUint32)),
        Member(176, "specularMultiplier", hkReal),
        Member(180, "specularExponent", hkReal),
        Member(184, "transparency", hkEnum(hkxMaterialTransparency, hkUint8)),
        Member(192, "userData", hkUlong),
        Member(200, "properties", hkArray(hkxMaterialProperty)),
    )
    members = hkxAttributeHolder.members + local_members

    name: str
    stages: list[hkxMaterialTextureStage]
    diffuseColor: Vector4
    ambientColor: Vector4
    specularColor: Vector4
    emissiveColor: Vector4
    subMaterials: list[hkxMaterial]
    extraData: hkReferencedObject
    uvMapScale: tuple[float, ...]
    uvMapOffset: tuple[float, ...]
    uvMapRotation: float
    uvMapAlgorithm: int
    specularMultiplier: float
    specularExponent: float
    transparency: int
    userData: int
    properties: list[hkxMaterialProperty]
