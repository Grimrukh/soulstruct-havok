from __future__ import annotations

__all__ = [
    "AnimationHKX",
    "SkeletonHKX",
    "CollisionHKX",
    "ClothHKX",
    "RagdollHKX",
    "RemoAnimationHKX",
    "MapCollisionHKX",
]

import logging
import subprocess as sp
import typing as tp
from dataclasses import dataclass
from pathlib import Path

from soulstruct.containers import DCXType

from soulstruct_havok.core import HavokFileFormat
from soulstruct_havok.packfile.structs import PackFileVersion, PackfileHeaderInfo
from soulstruct_havok.types import hk, hk2010, hk2015
from soulstruct_havok.types.hk2015 import *
from soulstruct_havok.wrappers.base import *
from soulstruct_havok.wrappers.base.file_types import (
    BaseWrappedHKX,
    AnimationHKX as BaseAnimationHKX,
    SkeletonHKX as BaseSkeletonHKX,
    ClothHKX as BaseClothHKX,
    RagdollHKX as BaseRagdollHKX,
    RemoAnimationHKX as BaseRemoAnimationHKX,
    CollisionHKX as BaseCollisionHKX,
)
from soulstruct_havok.wrappers.base.type_vars import PHYSICS_DATA_T
from soulstruct_havok.wrappers.hkx2010 import AnimationHKX as AnimationHKX2010
from soulstruct_havok.utilities.hk_conversion import convert_hk
from soulstruct_havok.utilities.wavefront import read_obj

from .physics import MapCollisionPhysicsData

_LOGGER = logging.getLogger(__name__)

AnimationContainerType = AnimationContainer[
    hkaAnimationContainer, hkaAnimation, hkaAnimationBinding,
    hkaInterleavedUncompressedAnimation, hkaSplineCompressedAnimation, hkaDefaultAnimatedReferenceFrame,
]
SkeletonType = Skeleton[hkaSkeleton, hkaBone]
SkeletonMapperType = SkeletonMapper[hkaSkeletonMapperData]
PhysicsDataType = PhysicsData[hkpPhysicsData, hkpPhysicsSystem]

# Mesh data typing: a tuple of `(vertices_list, face_indices_list)`.
MESH_TYPING = tp.Tuple[list[Vector4 | tp.Sequence[float]], list[tp.Sequence[int]]]


@dataclass(slots=True)
class AnimationHKX(BaseAnimationHKX):
    TYPES_MODULE: tp.ClassVar = hk2015
    root: hkRootLevelContainer = None
    animation_container: AnimationContainerType = None

    def to_spline_animation(self) -> AnimationHKX:
        """Uses Horkrux's compiled converter to convert interleaved to spline.

        Returns an entire new Havok 2010 instance of an `AnimationHKX` file.
        """
        if not self.animation_container.is_interleaved:
            raise TypeError("Can only convert interleaved animations to spline animations.")
        _LOGGER.debug("Downgrading to 2010...")
        hkx2010 = self.to_2010_hkx()
        _LOGGER.debug("Writing 2010 file...")
        hkx2010.write("__temp_interleaved__.hkx")
        _LOGGER.debug("Calling `CompressAnim`...")
        ret_code = sp.call(
            ["C:\\Dark Souls\\CompressAnim.exe", "__temp_interleaved__.hkx", "__temp_spline__.hkx", "1", "0.001"]
        )
        _LOGGER.debug(f"Done. Return code: {ret_code}")
        if ret_code != 0:
            raise RuntimeError(f"`CompressAnim.exe` had return code {ret_code}.")
        _LOGGER.debug("Reading 2010 spline-compressed animation...")
        hkx2010_spline = AnimationHKX2010.from_path("__temp_spline__.hkx")
        _LOGGER.debug("Upgrading to 2015...")
        anim_2015 = AnimationHKX.from_2010_hkx(hkx2010_spline)
        _LOGGER.info("Successfully converted interleaved animation to hk2015 spline animation.")
        return anim_2015

    def to_2010_hkx(self) -> AnimationHKX2010:
        """Construct a 2010 Havok file (with packfile type) from this 2015 tagfile.

        This is done using Capra Demon's animation 3000 from PTDE as a base, and injecting this file's data into it.

        (I am adding these specific conversion functions as needed for Nightfall.)
        """
        if self.animation_container.is_spline:
            self.animation_container.save_spline_data()
        elif self.animation_container.is_interleaved:
            self.animation_container.save_interleaved_data()

        def source_handler(_, name: str, value, dest: hk):
            if name == "refCount":
                setattr(dest, "referenceCount", value)
                return ["referenceCount"]
            if name in ("partitionIndices", "frameType"):  # absent from 2010
                return []

        import time
        t = time.perf_counter()
        root2010 = convert_hk(self.root, hk2010.hkRootLevelContainer, hk2010, source_handler)
        print(f"2015 to 2010 time: {time.perf_counter() - t}")
        return AnimationHKX2010(
            root=root2010,
            hk_format=HavokFileFormat.Packfile,
            hk_version="2010",
            packfile_header_info=PackfileHeaderInfo(
                header_version=PackFileVersion.Version0x08,
                pointer_size=4,
                is_little_endian=True,
                padding_option=0,
                contents_version_string=b"hk_2010.2.0-r1",
                flags=0,
                header_extension=None,
            ),
        )

    @classmethod
    def from_2010_hkx(cls, hkx2010: AnimationHKX2010) -> AnimationHKX:

        def source_handler(_, name: str, value, dest: hk):
            if name == "referenceCount":
                setattr(dest, "refCount", value)
                return ["refCount"]

        def dest_handler(dest: hk, name: str):
            if isinstance(dest, hk2015.hkaAnimationBinding) and name == "partitionIndices":
                dest.partitionIndices = []
                return True
            return False

        import time
        t = time.perf_counter()
        root2015 = convert_hk(hkx2010.root, hk2015.hkRootLevelContainer, hk2015, source_handler, dest_handler)
        print(f"2015 to 2010 time: {time.perf_counter() - t}")
        return cls(root=root2015, hk_format=HavokFileFormat.Tagfile, hk_version="2015")


@dataclass(slots=True)
class SkeletonHKX(BaseSkeletonHKX):
    TYPES_MODULE: tp.ClassVar = hk2015
    root: hkRootLevelContainer = None
    skeleton: SkeletonType = None


@dataclass(slots=True)
class CollisionHKX(BaseCollisionHKX):
    TYPES_MODULE: tp.ClassVar = hk2015
    root: hkRootLevelContainer = None
    physics_data: PhysicsDataType = None


@dataclass(slots=True)
class ClothHKX(BaseClothHKX):
    TYPES_MODULE: tp.ClassVar = hk2015
    root: hkRootLevelContainer = None
    cloth_physics_data: ClothPhysicsData[hkpPhysicsData, hkpPhysicsSystem] = None


@dataclass(slots=True)
class RagdollHKX(BaseRagdollHKX):
    TYPES_MODULE: tp.ClassVar = hk2015
    root: hkRootLevelContainer = None
    standard_skeleton: SkeletonType = None
    ragdoll_skeleton: SkeletonType = None
    physics_data: PhysicsDataType = None
    ragdoll_to_standard_skeleton_mapper: SkeletonMapperType = None
    standard_to_ragdoll_skeleton_mapper: SkeletonMapperType = None


@dataclass(slots=True)
class RemoAnimationHKX(BaseRemoAnimationHKX):
    TYPES_MODULE: tp.ClassVar = hk2015
    root: hkRootLevelContainer = None
    animation_container: AnimationContainerType = None
    skeleton: SkeletonType = None


@dataclass(slots=True)
class MapCollisionHKX(BaseWrappedHKX):
    TYPES_MODULE: tp.ClassVar = hk2015
    root: hkRootLevelContainer = None
    map_collision_physics_data: MapCollisionPhysicsData = None

    def __post_init__(self):
        self.map_collision_physics_data = MapCollisionPhysicsData(
            self.TYPES_MODULE, self.get_variant(0, *PHYSICS_DATA_T.__constraints__))

    @classmethod
    def from_meshes(
        cls,
        meshes: list[MESH_TYPING],
        hkx_name: str,
        material_indices: tp.Sequence[int] = (),
        template_hkx: MapCollisionHKX = None,
        dcx_type: DCXType = None,
    ) -> MapCollisionHKX:
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
            template_path = Path(__file__).parent / "../../resources/MapCollisionTemplate2015.hkx"
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

        child_shape.cachedNumChildShapes = sum(len(faces) for _, faces in meshes)
        child_shape.trianglesSubparts = []
        child_shape.meshstorage = []
        child_shape.materialArray = []
        for i, (vertices, faces) in enumerate(meshes):

            subpart = cls.map_collision_physics_data.new_subpart(len(vertices), len(faces))
            child_shape.trianglesSubparts.append(subpart)

            indices = []
            for face in faces:
                indices.extend(face)
                if len(face) == 3:
                    indices.append(0)
            storage = hkpStorageExtendedMeshShapeMeshSubpartStorage(
                memSizeAndFlags=0,
                refCount=0,
                vertices=[Vector4((*v[:3], 0.0)) for v in vertices],
                indices8=[],
                indices16=indices,
                indices32=[],
                materialIndices=[],
                materials=[],
                namedMaterials=[],
                materialIndices16=[],
            )
            child_shape.meshstorage.append(storage)

            material = CustomMeshParameter(
                memSizeAndFlags=0,
                refCount=0,
                version=37120,
                vertexDataBuffer=[255] * len(vertices),
                vertexDataStride=1,
                primitiveDataBuffer=[],
                materialNameData=material_indices[i],
            )
            child_shape.materialArray.append(material)

        # Havok docs say that embedded triangle subpart is only efficient for single-subpart shapes, but FromSoft seems
        # to disagree (or just didn't care), because it is included for multi-mesh files. However, note, that the
        # embedded subpart is a fresh instance, not a copy of the first subpart.
        first_mesh_vertex_count = len(meshes[0][0])
        first_mesh_face_count = len(meshes[0][1])
        child_shape.embeddedTrianglesSubpart = cls.map_collision_physics_data.new_subpart(
            first_mesh_vertex_count, first_mesh_face_count
        )

        all_vertices = [v for mesh, _ in meshes for v in mesh]
        x_min = min([v[0] for v in all_vertices])
        x_max = max([v[0] for v in all_vertices])
        y_min = min([v[1] for v in all_vertices])
        y_max = max([v[1] for v in all_vertices])
        z_min = min([v[2] for v in all_vertices])
        z_max = max([v[2] for v in all_vertices])
        child_shape.aabbHalfExtents = Vector4([(x_max - x_min) / 2, (y_max - y_min) / 2, (z_max - z_min) / 2, 0.0])
        child_shape.aabbCenter = Vector4([(x_max + x_min) / 2, (y_max + y_min) / 2, (z_max + z_min) / 2, 0.0])

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
        template_hkx: MapCollisionHKX = None,
        invert_x=True,
        dcx_type: DCXType = DCXType.Null,
    ) -> MapCollisionHKX:
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

    def to_meshes(self) -> list[tuple[list[tuple[float, float, float]], list[tuple[int, int, int]]]]:
        """Get a list of subpart meshes. Each is a list of vertices (three floats) and a list of face index triples."""
        meshes = []
        for mesh in self.map_collision_physics_data.get_extended_mesh_meshstorage():
            if len(mesh.indices16) % 4:
                raise ValueError("`indices16` length must be a multiple of 4.")
            vertices = [(vert.x, vert.y, vert.z) for vert in mesh.vertices]
            faces = []
            for f in range(len(mesh.indices16) // 4):
                index_0 = mesh.indices16[4 * f]
                index_1 = mesh.indices16[4 * f + 1]
                index_2 = mesh.indices16[4 * f + 2]
                # NOTE: Index 3 in `mesh.indices16` quadruples is always 0, so we ignore it.
                faces.append((index_0, index_1, index_2))
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
