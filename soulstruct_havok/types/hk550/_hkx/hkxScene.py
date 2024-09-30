from __future__ import annotations

from dataclasses import dataclass

from soulstruct_havok.enums import *
from ..core import *
from .hkxMaterial import hkxMaterial
from .hkxNode import hkxNode


@dataclass(slots=True, eq=False, repr=False, kw_only=True)
class hkxScene(hk):
    alignment = 16
    byte_size = 192
    tag_type_flags = TagDataType.Class

    __tag_format_flags = 41

    local_members = (
        Member(0, "modeller", hkStringPtr),
        Member(4, "asset", hkStringPtr),
        Member(8, "sceneLength", hkReal),
        Member(12, "rootNode", Ptr(hkReflectDetailOpaque)),  # TODO: Ptr(hkxNode)),
        Member(16, "selectionSets", hkArray(Ptr(hkReflectDetailOpaque))),  # TODO: hkArray(Ptr(hkxNodeSelectionSet))),
        Member(28, "numSelectionSets", hkInt32),
        Member(32, "cameras", hkArray(Ptr(hkReflectDetailOpaque))),  # TODO: hkArray(Ptr(hkxCamera))),
        Member(44, "numCameras", hkInt32),
        Member(48, "lights", hkArray(Ptr(hkReflectDetailOpaque))),  # TODO: hkArray(Ptr(hkxLight))),
        Member(60, "numLights", hkInt32),
        Member(64, "meshes", hkArray(Ptr(hkReflectDetailOpaque))),  # TODO: hkArray(Ptr(hkxMesh))),
        Member(76, "numMeshes", hkInt32),
        Member(80, "materials", hkArray(Ptr(hkxMaterial))),
        Member(92, "numMaterials", hkInt32),
        Member(96, "inplaceTextures", hkArray(Ptr(hkReflectDetailOpaque))),  # TODO: hkArray(Ptr(hkxTextureInplace))),
        Member(108, "numInplaceTextures", hkInt32),
        Member(112, "externalTextures", hkArray(Ptr(hkReflectDetailOpaque))),  # TODO: hkArray(Ptr(hkxTextureFile))),
        Member(124, "numExternalTextures", hkInt32),
        Member(128, "skinBindings", hkArray(Ptr(hkReflectDetailOpaque))),  # TODO: hkArray(Ptr(hkxSkinBinding))),
        Member(140, "numSkinBindings", hkInt32),
        Member(144, "appliedTransform", hkMatrix3),
    )
    members = local_members

    modeller: str
    asset: str
    sceneLength: float
    rootNode: hkxNode
    selectionSets: list[None]
    numSelectionSets: str
    cameras: list[None]
    numCameras: int
    lights: list[None]
    numLights: int
    meshes: list[None]
    numMeshes: int
    materials: list[hkxMaterial]
    numMaterials: int
    inplaceTextures: list[None]
    numInplaceTextures: int
    externalTextures: list[None]
    numExternalTextures: int
    skinBindings: list[None]
    numSkinBindings: int
    appliedTransform: hkMatrix3
