from __future__ import annotations

import logging
import typing as tp

from soulstruct_havok.types.hk2015 import *
from soulstruct_havok.utilities.mopper import mopper
from soulstruct_havok.utilities.maths import Vector4, Quaternion
from soulstruct_havok.wrappers.base.physics import PhysicsData

_LOGGER = logging.getLogger(__name__)


class MapCollisionPhysicsData(PhysicsData[hkpPhysicsData, hkpPhysicsSystem]):
    """FromSoft map collisions use a custom shape data container called `CustomParamStorageExtendedMeshShape`, which
    gives each mesh a material ID that determines footstep sounds/VFX and other interactive properties.

    Each mesh has a special MOPP code that is generated by Havok to speed up collision detection. The MOPP code is
    stored in the `hkpMoppBvTreeShape` shape and is regenerated here using a bundled executable I compiled from the
    public Havok 2012 SDK, modified from a Niftools repo.

    Note that the name of the map collision is also stored inside the shape data.

    I'm not sure if games after (or before) DS1 use the MOPP code -- I suspect some of them use new `hknp` classes with
    even less scrutable detection methods -- so this class is attached to Havok 2015 (DSR) for now.
    """

    def get_child_shape(self) -> CustomParamStorageExtendedMeshShape:
        """Validates type of collision shape and returns `childShape`."""
        shape = self.physics_system.rigidBodies[0].collidable.shape
        if not isinstance(shape, hkpMoppBvTreeShape):
            raise TypeError("Expected collision shape to be `hkpMoppBvTreeShape`.")
        child_shape = shape.child.childShape
        if not isinstance(child_shape, CustomParamStorageExtendedMeshShape):
            raise TypeError("Expected collision child shape to be `CustomParamStorageExtendedMeshShape`.")
        return child_shape

    def get_extended_mesh_meshstorage(self) -> list[hkpStorageExtendedMeshShapeMeshSubpartStorage]:
        """Validates type of collision shape and returns `meshstorage` member."""
        return self.get_child_shape().meshstorage

    def get_mopp_code(self) -> hkpMoppCode:
        shape = self.physics_system.rigidBodies[0].collidable.shape
        if not isinstance(shape, hkpMoppBvTreeShape):
            raise TypeError("Expected collision shape to be `hkpMoppBvTreeShape`.")
        return shape.code

    def get_subpart_materials(self) -> tuple[int]:
        """Returns a tuple of `materialNameData` integers, one for each subpart mesh."""
        child_shape = self.get_child_shape()
        return tuple(material.materialNameData for material in child_shape.materialArray)

    def set_subpart_materials(self, material_indices: tp.Sequence[int]):
        child_shape = self.get_child_shape()
        if len(material_indices) != len(child_shape.materialArray):
            raise ValueError(
                f"Number of given material indices ({len(material_indices)}) "
                f"!= number of HKX materials {len(child_shape.materialArray)})."
            )
        for material, new_index in zip(child_shape.materialArray, material_indices, strict=True):
            material.materialNameData = new_index

    def regenerate_mopp_data(self):
        """Use `mopper.exe` to build new MOPP code, including `code.info.offset` vector."""
        meshstorage = self.get_extended_mesh_meshstorage()
        mopp_code = self.get_mopp_code()

        mopper_input = [f"{len(meshstorage)}"]
        for mesh in meshstorage:
            mopper_input.append("")
            mopper_input.append(f"{len(mesh.vertices)}")
            for v in mesh.vertices:
                mopper_input.append(f"{v.x} {v.y} {v.z}")
            mopper_input.append("")
            mopper_input.append(f"{len(mesh.indices16) // 4}")
            faces = mesh.indices16.copy()
            while faces:
                mopper_input.append(f"{faces[0]} {faces[1]} {faces[2]}")
                faces = faces[4:]  # drop 0 after triple

        mopp = mopper(mopper_input, mode="-esm")
        new_mopp_code = mopp["hkpMoppCode"]["data"]
        new_offset = mopp["hkpMoppCode"]["offset"]
        mopp_code.data = new_mopp_code
        mopp_code.info.offset = Vector4(new_offset)

    def get_name(self) -> str:
        return self.physics_system.rigidBodies[0].name

    @staticmethod
    def new_subpart(vertices_count: int, faces_count: int):
        """Returns a new `hkpExtendedMeshShapeTrianglesSubpart` with the given number of vertices and faces.

        All other members can be set to default values, fortunately (in DS1 at least).

        TODO: `triangleOffset` can probably be extracted from Mopper output. It doesn't seem to matter, though.
        """
        return hkpExtendedMeshShapeTrianglesSubpart(
            typeAndFlags=2,
            shapeInfo=0,
            materialIndexBase=None,
            materialBase=None,
            vertexBase=None,
            indexBase=None,
            materialStriding=0,
            materialIndexStriding=0,
            userData=0,
            numTriangleShapes=faces_count,
            numVertices=vertices_count,
            vertexStriding=16,
            triangleOffset=2010252431,  # TODO: should be given in `mopp.json`
            indexStriding=8,
            stridingType=2,  # 16-bit
            flipAlternateTriangles=0,
            extrusion=Vector4.zero(),
            transform=hkQsTransform(
                translation=Vector4.zero(),
                rotation=Quaternion.identity(),
                scale=Vector4.one(),
            ),
        )