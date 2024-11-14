from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *
from .hkxMaterial import hkxMaterial
from .hkxNode import hkxNode
from .hkxNodeSelectionSet import hkxNodeSelectionSet
from .hkxCamera import hkxCamera
from .hkxLight import hkxLight
from .hkxMesh import hkxMesh
from .hkxTextureInplace import hkxTextureInplace
from .hkxTextureFile import hkxTextureFile
from .hkxSkinBinding import hkxSkinBinding


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkxScene(hk):
    alignment = 16
    byte_size = 128
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41
    __hsh = 531768161

    local_members = (
        Member(0, "modeller", hkStringPtr),
        Member(4, "asset", hkStringPtr),
        Member(8, "sceneLength", hkReal),
        Member(12, "rootNode", Ptr(hkxNode)),
        Member(16, "selectionSets", SimpleArray(Ptr(hkxNodeSelectionSet))),
        Member(24, "cameras", SimpleArray(Ptr(hkxCamera))),
        Member(32, "lights", SimpleArray(Ptr(hkxLight))),
        Member(40, "meshes", SimpleArray(Ptr(hkxMesh))),
        Member(48, "materials", SimpleArray(Ptr(hkxMaterial))),
        Member(56, "inplaceTextures", SimpleArray(Ptr(hkxTextureInplace))),
        Member(64, "externalTextures", SimpleArray(Ptr(hkxTextureFile))),
        Member(72, "skinBindings", SimpleArray(Ptr(hkxSkinBinding))),
        Member(80, "appliedTransform", hkMatrix3),
    )
    members = local_members

    modeller: str
    asset: str
    sceneLength: float
    rootNode: hkxNode
    selectionSets: list[hkxNodeSelectionSet]
    cameras: list[hkxCamera]
    lights: list[hkxLight]
    meshes: list[hkxMesh]
    materials: list[hkxMaterial]
    inplaceTextures: list[hkxTextureInplace]
    externalTextures: list[hkxTextureFile]
    skinBindings: list[hkxSkinBinding]
    appliedTransform: hkMatrix3
