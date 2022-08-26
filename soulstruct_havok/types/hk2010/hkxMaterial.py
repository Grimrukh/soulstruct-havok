from __future__ import annotations

from soulstruct_havok.types.core import *
from soulstruct_havok.enums import *
from .core import *
from .hkxAttributeHolder import hkxAttributeHolder
from .hkxMaterialTextureStage import hkxMaterialTextureStage
from .hkxMaterialProperty import hkxMaterialProperty


class hkxMaterial(hkxAttributeHolder):
    alignment = 16
    byte_size = 144
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(20, "name", hkStringPtr),
        Member(24, "stages", hkArray(hkxMaterialTextureStage)),
        Member(48, "diffuseColor", hkVector4),
        Member(64, "ambientColor", hkVector4),
        Member(80, "specularColor", hkVector4),
        Member(96, "emissiveColor", hkVector4),
        Member(112, "subMaterials", hkArray(Ptr(DefType("hkxMaterial", lambda: hkxMaterial)))),
        Member(124, "extraData", Ptr(hkReferencedObject)),
        Member(128, "properties", hkArray(hkxMaterialProperty)),
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
    properties: list[hkxMaterialProperty]
