from __future__ import annotations

from dataclasses import dataclass, field

from soulstruct.havok.enums import *
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
    rootNode: hkxNode | None = None
    selectionSets: list[hkxNodeSelectionSet] = field(default_factory=list)
    cameras: list[hkxCamera] = field(default_factory=list)
    lights: list[hkxLight] = field(default_factory=list)
    meshes: list[hkxMesh] = field(default_factory=list)
    materials: list[hkxMaterial] = field(default_factory=list)
    inplaceTextures: list[hkxTextureInplace] = field(default_factory=list)
    externalTextures: list[hkxTextureFile] = field(default_factory=list)
    skinBindings: list[hkxSkinBinding] = field(default_factory=list)
    # NOTE: Default transform swaps Y and Z axes, which likely indicates From's export settings from 3DS Max.
    appliedTransform: tuple[float, ...] = (1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 1.0, 0.0, 0.0, 1.0, 0.0, 0.0)
