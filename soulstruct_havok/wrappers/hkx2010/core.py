from __future__ import annotations

__all__ = ["AnimationHKX", "SkeletonHKX", "ClothHKX", "RagdollHKX", "MapCollisionHKX"]

import logging
import typing as tp
from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path

import numpy as np
from soulstruct.dcx import DCXType

from soulstruct_havok.types import hk2010
from soulstruct_havok.types.hk2010 import *
from soulstruct_havok.wrappers.base import *
from soulstruct_havok.utilities.files import HAVOK_PACKAGE_PATH
from soulstruct_havok.utilities.wavefront import read_obj
from soulstruct_havok.wrappers.base.type_vars import PHYSICS_DATA_T
from .physics import MapCollisionPhysicsData

AnimationContainerType = AnimationContainer[
    hkaAnimationContainer, hkaAnimation, hkaAnimationBinding,
    hkaInterleavedUncompressedAnimation, hkaSplineCompressedAnimation, hkaDefaultAnimatedReferenceFrame,
]
SkeletonType = Skeleton[hkaSkeleton, hkaBone]
SkeletonMapperType = SkeletonMapper[hkaSkeletonMapper]
PhysicsDataType = PhysicsData[hkpPhysicsData, hkpPhysicsSystem]

_LOGGER = logging.getLogger("soulstruct_havok")


@dataclass(slots=True, repr=False)
class AnimationHKX(BaseAnimationHKX):
    TYPES_MODULE = hk2010
    root: hkRootLevelContainer = None
    animation_container: AnimationContainerType = None


@dataclass(slots=True, repr=False)
class SkeletonHKX(BaseSkeletonHKX):
    TYPES_MODULE = hk2010
    root: hkRootLevelContainer = None
    skeleton: SkeletonType = None


@dataclass(slots=True, repr=False)
class CollisionHKX(BaseCollisionHKX):
    TYPES_MODULE = hk2010
    root: hkRootLevelContainer = None
    physics_data: PhysicsDataType = None


@dataclass(slots=True, repr=False)
class ClothHKX(BaseClothHKX):
    TYPES_MODULE = hk2010
    root: hkRootLevelContainer = None
    cloth_physics_data: ClothPhysicsData[hkpPhysicsData, hkpPhysicsSystem] = None


@dataclass(slots=True, repr=False)
class RagdollHKX(BaseRagdollHKX):
    TYPES_MODULE = hk2010
    root: hkRootLevelContainer = None
    animation_skeleton: SkeletonType = None
    ragdoll_skeleton: SkeletonType = None
    physics_data: PhysicsDataType = None
    animation_to_ragdoll_skeleton_mapper: SkeletonMapperType = None
    ragdoll_to_animation_skeleton_mapper: SkeletonMapperType = None


@dataclass(slots=True)
class MapCollisionHKX(BaseWrappedHKX):
    """TODO: Shares 99% of code with 2015 (DSR) version. Move to shared location in `base`."""
    TYPES_MODULE: tp.ClassVar = hk2010
    root: hkRootLevelContainer = None
    map_collision_physics_data: MapCollisionPhysicsData = None

    class MapCollisionMaterial(IntEnum):
        Default = 0  # unknown usage
        Rock = 1  # actual rocks, bricks
        Stone = 2  # e.g. walls
        Grass = 3  # e.g. forest ground
        Wood = 4  # e.g. logs
        LoResGround = 5  # unknown purpose; seems to randomly replace other ground types in lo-res
        # TODO: 6 appears in h1000B2A10 (Firelink).
        Metal = 9  # e.g. grilles

        # rough
        ShallowWater = 20
        DeepWater = 21
        Killplane = 29  # or deathcam trigger, or lethal fall, etc.
        Trigger = 40  # other triggers?

        # NOTE: Offsets of 100, 200, and 300 appear to be used for stairs/sloped submeshes?

    def __post_init__(self):
        self.map_collision_physics_data = MapCollisionPhysicsData(
            self.TYPES_MODULE, self.get_variant(0, *PHYSICS_DATA_T.__constraints__))

    @classmethod
    def from_meshes(
        cls,
        meshes: list[tuple[np.ndarray, np.ndarray]],
        hkx_name: str,
        material_indices: tp.Sequence[int] = (),
        template_hkx: tp.Self = None,
        dcx_type: DCXType = None,
    ) -> tp.Self:
        """Convert a list of subpart meshes (vertices and faces) to a HKX collision file.

        Uses an existing HKX template file rather than constructing one from scratch. A custom template may also be
        supplied with `template_hkx`. Note that this custom template will be modified in place AND returned, not copied.

        Also uses default values for new mesh Havok classes, most of which don't matter or are empty. The one non-mesh
        property that really matters is `materialNameData`, which determines the material of the collision (for sounds,
        footsteps, terrain params, etc.) and can be supplied manually with `material_indices`. If given,
        `material_indices` must be a tuple with the same length as `meshes` (one material index per subpart).
        """
        if not meshes:
            raise ValueError("At least one mesh must given to `from_meshes()`.")

        if template_hkx is None:
            # Use bundled template.
            template_path = HAVOK_PACKAGE_PATH("resources/MapCollisionTemplate2010.hkx")
            hkx = cls.from_path(template_path)
        else:
            hkx = template_hkx
        child_shape = hkx.map_collision_physics_data.get_child_shape()

        if not material_indices:
            # Use material data from template.
            material_indices = [material.materialNameData for material in child_shape.materialArray]
            if len(material_indices) < len(meshes):
                extra_mesh_count = len(meshes) - len(material_indices)
                _LOGGER.warning(f"Adding material index 0 for {extra_mesh_count} extra meshes added to template HKX.")
                material_indices += [0] * extra_mesh_count
            while len(material_indices) < len(meshes):
                material_indices.append(0)
        elif len(material_indices) != len(meshes):
            raise ValueError(
                f"Length of `material_name_data` ({len(material_indices)}) does not match number of meshes in "
                f"OBJ ({len(meshes)})."
            )

        rigid_body = hkx.map_collision_physics_data.physics_system.rigidBodies[0]
        rigid_body.name = hkx_name

        # TODO: rigid_body.motion.motionState.objectRadius?

        total_face_count = sum(faces.shape[0] for _, faces in meshes)
        child_shape.cachedNumChildShapes = total_face_count
        child_shape.trianglesSubparts = []
        child_shape.meshstorage = []
        child_shape.materialArray = []

        for col_material_index, (vertices, faces) in zip(material_indices, meshes):

            subpart = hkx.map_collision_physics_data.new_subpart(len(vertices), len(faces))
            child_shape.trianglesSubparts.append(subpart)

            if vertices.shape[1] == 3:
                # Add fourth column of zeroes.
                vertices = np.hstack((vertices, np.zeros((vertices.shape[0], 1), dtype=vertices.dtype)))

            if faces.shape[1] == 3:
                # Add fourth column of zeroes.
                faces = np.hstack((faces, np.zeros((faces.shape[0], 1), dtype=faces.dtype)))

            storage = hkpStorageExtendedMeshShapeMeshSubpartStorage(
                memSizeAndFlags=0,
                referenceCount=0,  # TODO: 'refCount' in 2015
                vertices=vertices,
                indices8=[],
                indices16=faces.ravel().tolist(),
                indices32=[],
                materialIndices=[],
                materials=[],
                namedMaterials=[],
                materialIndices16=[],
            )
            child_shape.meshstorage.append(storage)

            material = CustomMeshParameter(
                memSizeAndFlags=0,
                referenceCount=0,  # TODO: 'refCount' in 2015
                version=37120,
                vertexDataBuffer=[255] * vertices.shape[0],
                vertexDataStride=1,
                primitiveDataBuffer=[],
                materialNameData=col_material_index,
            )
            child_shape.materialArray.append(material)

        # Havok docs say that embedded triangle subpart is only efficient for single-subpart shapes, but FromSoft seems
        # to disagree (or just didn't care), because it is included for multi-mesh files. However, note, that the
        # embedded subpart is a fresh instance, not a copy of the first subpart.
        first_mesh_vertex_count = meshes[0][0].shape[0]
        first_mesh_face_count = meshes[0][1].shape[0]
        child_shape.embeddedTrianglesSubpart = hkx.map_collision_physics_data.new_subpart(
            first_mesh_vertex_count, first_mesh_face_count
        )

        vertex_mins = [vertices.min(axis=0) for vertices, _ in meshes]
        vertex_maxs = [vertices.max(axis=0) for vertices, _ in meshes]
        global_min = np.min(vertex_mins, axis=0)
        global_max = np.max(vertex_maxs, axis=0)
        half_extents = (global_max - global_min) / 2
        center = (global_max + global_min) / 2

        child_shape.aabbHalfExtents = Vector4([*half_extents, 0.0])
        child_shape.aabbCenter = Vector4([*center, 0.0])

        # Use Mopper executable to regenerate binary MOPP code.
        hkx.map_collision_physics_data.regenerate_mopp_data()

        hkx.dcx_type = dcx_type

        return hkx

    @classmethod
    def from_obj(
        cls,
        obj_path: Path | str,
        hkx_name: str,
        material_indices: tuple[int] = (),
        template_hkx: tp.Self = None,
        invert_x=True,
        dcx_type: DCXType = DCXType.Null,
    ) -> tp.Self:
        """Create a HKX from a template (defaults to package template) and subpart meshes in an OBJ file.

        `invert_x=True` by default, which should also be done in `to_obj()` if used again here (for accurate depiction
        in Blender, etc.).
        """
        obj_meshes = read_obj(obj_path, invert_x=invert_x)
        if not obj_meshes:
            raise ValueError("At least one mesh required in OBJ to convert to HKX.")
        return cls.from_meshes(
            obj_meshes,
            hkx_name=hkx_name,
            material_indices=material_indices,
            template_hkx=template_hkx,
            dcx_type=dcx_type,
        )

    def to_meshes(self) -> list[tuple[np.ndarray, np.ndarray]]:
        """Get a list of subpart meshes, as pairs of vertex and face arrays."""
        meshes = []
        for mesh in self.map_collision_physics_data.get_extended_mesh_meshstorage():
            if len(mesh.indices16) % 4:
                raise ValueError("`indices16` length must be a multiple of 4.")
            vertices = mesh.vertices[:, :3]  # drop fourth column
            face_count = len(mesh.indices16) // 4
            faces = np.empty((face_count, 3), dtype=np.uint16)
            for f in range(face_count):
                index_0 = mesh.indices16[4 * f]
                index_1 = mesh.indices16[4 * f + 1]
                index_2 = mesh.indices16[4 * f + 2]
                # NOTE: Index 3 in `mesh.indices16` quadruples is always 0, so we ignore it.
                faces[f] = [index_0, index_1, index_2]
            meshes.append((vertices, faces))
        return meshes

    def to_obj(self, invert_x=True) -> str:
        """Convert raw vertices and triangle faces (zero-separated triplets) from HKX meshes to OBJ file.

        Inverts (negates) X axis by default, which should be reversed on import.

        Also note that vertices in OBJ files are 1-indexed by the face indices.

        TODO: Would be nice to include the material indices.
        """
        name = self.map_collision_physics_data.get_name()
        obj_lines = [
            f"# OBJ file generated by Soulstruct from HKX with path: {self.path}",
            f"# Internal name: {name}"
        ]
        global_v_i = 0

        for i, mesh in enumerate(self.map_collision_physics_data.get_extended_mesh_meshstorage()):
            if len(mesh.indices16) % 4:
                raise ValueError("`indices16` length must be a multiple of 4.")
            obj_lines += ["", f"o {name} Subpart {i}"]
            for vert in mesh.vertices:
                obj_lines.append(f"v {-vert.x if invert_x else vert.x} {vert.y} {vert.z}")
            obj_lines.append("s off")
            for f in range(len(mesh.indices16) // 4):
                face = mesh.indices16[4 * f:4 * f + 3]
                obj_lines.append(
                    f"f {face[0] + global_v_i + 1} {face[1] + global_v_i + 1} {face[2] + global_v_i + 1}"
                )  # note 1-indexing of vertices in OBJ faces
            global_v_i += len(mesh.vertices)

        return "\n".join(obj_lines) + "\n"

    def write_obj(self, obj_path: Path | str):
        """Write OBJ file to `obj_path`."""
        Path(obj_path).write_text(self.to_obj())
