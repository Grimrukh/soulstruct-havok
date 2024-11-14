from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *
from .hkxAttributeHolder import hkxAttributeHolder
from .hkxMaterialTextureStage import hkxMaterialTextureStage


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkxMaterial(hkxAttributeHolder):
    alignment = 16
    byte_size = 108
    tag_type_flags = TagDataType.Class
    __hsh = 4075555996

    __tag_format_flags = 41

    local_members = (
        Member(8, "name", hkStringPtr),
        Member(12, "stages", SimpleArray(hkxMaterialTextureStage)),
        Member(32, "diffuseColor", hkVector4),
        Member(48, "ambientColor", hkVector4),
        Member(64, "specularColor", hkVector4),
        Member(80, "emissiveColor", hkVector4),
        Member(96, "subMaterials", SimpleArray(Ptr(DefType("hkxMaterial", lambda: hkxMaterial)))),
        Member(104, "extraData", Ptr(hkReferencedObject)),  # `hkVariant.m_class`
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
