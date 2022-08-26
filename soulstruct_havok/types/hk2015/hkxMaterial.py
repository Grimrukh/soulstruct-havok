from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *
from .hkxAttributeHolder import hkxAttributeHolder
from .hkxMaterialTextureStage import hkxMaterialTextureStage
from .hkxMaterialUVMappingAlgorithm import hkxMaterialUVMappingAlgorithm
from .hkxMaterialTransparency import hkxMaterialTransparency
from .hkxMaterialProperty import hkxMaterialProperty


class hkxMaterial(hkxAttributeHolder):
    alignment = 16
    byte_size = 224
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 45
    __version = 5

    local_members = (
        Member(32, "name", hkStringPtr),
        Member(40, "stages", hkArray(hkxMaterialTextureStage)),
        Member(64, "diffuseColor", hkVector4),
        Member(80, "ambientColor", hkVector4),
        Member(96, "specularColor", hkVector4),
        Member(112, "emissiveColor", hkVector4),
        Member(128, "subMaterials", hkArray(hkRefPtr(DefType("hkxMaterial", lambda: hkxMaterial)))),
        Member(144, "extraData", hkRefVariant(hkReferencedObject, hsh=2872857893)),
        Member(152, "uvMapScale", hkGenericStruct(hkReal, 2)),
        Member(160, "uvMapOffset", hkGenericStruct(hkReal, 2)),
        Member(168, "uvMapRotation", hkReal),
        Member(172, "uvMapAlgorithm", hkEnum(hkxMaterialUVMappingAlgorithm, hkUint32)),
        Member(176, "specularMultiplier", hkReal),
        Member(180, "specularExponent", hkReal),
        Member(184, "transparency", hkEnum(hkxMaterialTransparency, hkUint8)),
        Member(192, "userData", hkUlong),
        Member(200, "properties", hkArray(hkxMaterialProperty), MemberFlags.Protected),
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
    uvMapScale: tuple[hkReal]
    uvMapOffset: tuple[hkReal]
    uvMapRotation: float
    uvMapAlgorithm: hkxMaterialUVMappingAlgorithm
    specularMultiplier: float
    specularExponent: float
    transparency: hkxMaterialTransparency
    userData: int
    properties: list[hkxMaterialProperty]
