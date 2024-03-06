from __future__ import annotations

__all__ = [
    "AnimationHKX",
    "SkeletonHKX",
    "CollisionHKX",
    "ClothHKX",
    "RagdollHKX",
    "RemoAnimationHKX",
    "MapCollisionHKX",
    "AnimationContainerType",
    "SkeletonType",
    "SkeletonMapperType",
    "PhysicsDataType",
]

import logging
import subprocess as sp
import typing as tp
from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path

import numpy as np

from soulstruct.dcx import DCXType

from soulstruct_havok.core import HavokFileFormat
from soulstruct_havok.packfile.structs import PackFileVersion, PackfileHeaderInfo
from soulstruct_havok.types import hk2010, hk2016
from soulstruct_havok.types.hk2016 import *
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
from soulstruct_havok.utilities.files import HAVOK_PACKAGE_PATH
from soulstruct_havok.utilities.hk_conversion import convert_hk
from soulstruct_havok.utilities.maths import TRSTransform
from soulstruct_havok.utilities.wavefront import read_obj

from .physics import MapCollisionPhysicsData

_LOGGER = logging.getLogger("soulstruct_havok")

AnimationContainerType = AnimationContainer[
    hkaAnimationContainer, hkaAnimation, hkaAnimationBinding,
    hkaInterleavedUncompressedAnimation, hkaSplineCompressedAnimation, hkaDefaultAnimatedReferenceFrame,
]
SkeletonType = Skeleton[hkaSkeleton, hkaBone]
SkeletonMapperType = SkeletonMapper[hkaSkeletonMapperData]
PhysicsDataType = PhysicsData[hkpPhysicsData, hkpPhysicsSystem]


@dataclass(slots=True)
class AnimationHKX(BaseAnimationHKX):
    TYPES_MODULE: tp.ClassVar = hk2016
    root: hkRootLevelContainer = None
    animation_container: AnimationContainerType = None

    def get_spline_hkx(self) -> AnimationHKX:
        """Uses Horkrux's compiled converter to convert interleaved HKX to spline HKX.

        Returns an entire new instance of this class.
        """
        if not self.animation_container.is_interleaved:
            raise TypeError("Can only convert interleaved animations to spline animations.")

        temp_interleaved_path = HAVOK_PACKAGE_PATH("__temp_interleaved__.hkx")
        temp_spline_path = HAVOK_PACKAGE_PATH("__temp_spline__.hkx")

        dcx_type = self.dcx_type
        _LOGGER.debug("Downgrading to 2010...")
        hkx2010 = self.to_2010_hkx()
        try:
            _LOGGER.debug("Writing 2010 file...")
            hkx2010.write(temp_interleaved_path)
            _LOGGER.debug("Calling `CompressAnim`...")
            compress_anim_path = str(HAVOK_PACKAGE_PATH("resources/CompressAnim.exe"))
            ret_code = sp.call(
                [compress_anim_path, str(temp_interleaved_path), str(temp_spline_path), "1", "0.001"]
            )
            _LOGGER.debug(f"Done. Return code: {ret_code}")
            if ret_code != 0:
                raise RuntimeError(f"`CompressAnim.exe` had return code {ret_code}.")
            _LOGGER.debug("Reading 2010 spline-compressed animation...")
            hkx2010_spline = AnimationHKX2010.from_path(temp_spline_path)
        finally:
            temp_interleaved_path.unlink(missing_ok=True)
            temp_spline_path.unlink(missing_ok=True)

        _LOGGER.debug("Upgrading to 2015...")
        anim_2015 = self.__class__.from_2010_hkx(hkx2010_spline, dcx_type=dcx_type)

        # Clean-up: restore hash overrides, change binding to refer to same animation, and change animation type.
        anim_2015.hsh_overrides = self.hsh_overrides.copy()
        for i, anim in enumerate(anim_2015.animation_container.animation_container.animations):
            anim_2015.animation_container.animation_container.bindings[i].animation = anim
            anim.type = 3  # spline-compressed in Havok 2015 (was 5 in Havok 2010)

        _LOGGER.info("Successfully converted interleaved animation to hk2016 spline animation.")
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

        def source_error_handler(_, name: str, value, dest_kwargs: dict[str, tp.Any]):
            if name == "refCount":
                dest_kwargs["referenceCount"] = value
                return ["referenceCount"]
            if name in ("partitionIndices", "frameType"):  # absent from 2010
                return []

        import time
        t = time.perf_counter()
        root2010 = convert_hk(self.root, hk2010.hkRootLevelContainer, hk2010, source_error_handler)
        _LOGGER.info(f"Converted 2015 Animation HKX to 2010 in {time.perf_counter() - t} s.")
        return AnimationHKX2010(
            dcx_type=DCXType.Null,
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
    def from_2010_hkx(cls, hkx2010: AnimationHKX2010, dcx_type: DCXType = None) -> AnimationHKX:
        """Construct a 2015 Havok animation tagfile from a 2010 Havok animation packfile.

        `dcx_type` defaults to be the same as `hkx2010`. It does NOT default to the standard DSR DCX type, because most
        HKX files appear inside compressed binders and are NOT compressed themselves.
        """

        def source_handler(_, name: str, value, dest_kwargs: dict[str, tp.Any]):
            if name == "referenceCount":
                dest_kwargs["refCount"] = value
                return ["refCount"]

        def dest_handler(dest_type: type[hk], dest_kwargs: dict[str, tp.Any], name: str):
            if dest_type is hk2016.hkaAnimationBinding and name == "partitionIndices":
                dest_kwargs["partitionIndices"] = []
                return True
            return False

        if dcx_type is None:
            dcx_type = hkx2010.dcx_type

        import time
        t = time.perf_counter()
        root2015 = convert_hk(hkx2010.root, hk2016.hkRootLevelContainer, hk2016, source_handler, dest_handler)
        print(f"2010 to 2015 time: {time.perf_counter() - t}")
        return cls(
            dcx_type=dcx_type,
            root=root2015,
            hk_format=HavokFileFormat.Tagfile,
            hk_version="2015",
        )

    @classmethod
    def from_dsr_interleaved_template(
        cls,
        skeleton_hkx: SkeletonHKX,
        interleaved_data: list[list[TRSTransform]],
        transform_track_to_bone_indices: list[int] = None,
        root_motion: np.ndarray | None = None,
        is_armature_space=False,
    ) -> AnimationHKX:
        """Open bundled template HKX for Dark Souls Remastered (c2240, Capra Demon, animation 200).

        Arguments reflect the minimal data required to create a new animation from the template.
        """
        template_path = HAVOK_PACKAGE_PATH("resources/AnimationTemplate2015.hkx")
        hkx = cls.from_path(template_path)
        container = hkx.animation_container

        container.spline_to_interleaved()

        container.animation.duration = (len(interleaved_data) - 1) / 30.0  # TODO: assumes 30 FPS (always valid?)

        container.animation_binding.originalSkeletonName = skeleton_hkx.skeleton.skeleton.name
        if transform_track_to_bone_indices is None:
            # Default: same as bone order.
            transform_track_to_bone_indices = list(range(len(skeleton_hkx.skeleton.bones)))
        container.animation_binding.transformTrackToBoneIndices = transform_track_to_bone_indices
        container.animation.numberOfTransformTracks = len(transform_track_to_bone_indices)
        container.animation.annotationTracks = [
            hkaAnnotationTrack(
                trackName=skeleton_hkx.skeleton.bones[bone_index].name,
                annotations=[],
            )
            for bone_index in transform_track_to_bone_indices
        ]

        if is_armature_space:
            # NOTE: Must be called AFTER setting new transform track -> bone mapping above.
            container.set_interleaved_data_from_armature_space(skeleton_hkx.skeleton, interleaved_data)
        else:
            container.interleaved_data = interleaved_data
        container.save_interleaved_data()
        container.animation.floats = []

        if root_motion is None:
            hkx.animation_container.animation.extractedMotion = None
        else:  # template has some reference frame samples already
            hkx.animation_container.set_reference_frame_samples(root_motion)

        return hkx.get_spline_hkx()


@dataclass(slots=True)
class SkeletonHKX(BaseSkeletonHKX):
    TYPES_MODULE: tp.ClassVar = hk2016
    root: hkRootLevelContainer = None
    skeleton: SkeletonType = None


@dataclass(slots=True)
class CollisionHKX(BaseCollisionHKX):
    TYPES_MODULE: tp.ClassVar = hk2016
    root: hkRootLevelContainer = None
    physics_data: PhysicsDataType = None


@dataclass(slots=True)
class ClothHKX(BaseClothHKX):
    TYPES_MODULE: tp.ClassVar = hk2016
    root: hkRootLevelContainer = None
    cloth_physics_data: ClothPhysicsData[hkpPhysicsData, hkpPhysicsSystem] = None


@dataclass(slots=True)
class RagdollHKX(BaseRagdollHKX):
    TYPES_MODULE: tp.ClassVar = hk2016
    root: hkRootLevelContainer = None
    standard_skeleton: SkeletonType = None
    ragdoll_skeleton: SkeletonType = None
    physics_data: PhysicsDataType = None
    ragdoll_to_standard_skeleton_mapper: SkeletonMapperType = None
    standard_to_ragdoll_skeleton_mapper: SkeletonMapperType = None


@dataclass(slots=True)
class RemoAnimationHKX(BaseRemoAnimationHKX):
    TYPES_MODULE: tp.ClassVar = hk2016
    root: hkRootLevelContainer = None
    animation_container: AnimationContainerType = None
    skeleton: SkeletonType = None


@dataclass(slots=True)
class MapCollisionHKX(BaseWrappedHKX):
    TYPES_MODULE: tp.ClassVar = hk2016
    root: hkRootLevelContainer = None
    map_collision_physics_data: MapCollisionPhysicsData = None

    class MapCollisionMaterial(IntEnum):
        Default = 0  # unknown usage
        Rock = 1  # actual rocks, bricks
        Stone = 2  # e.g. walls
        Grass = 3  # e.g. forest ground
        Wood = 4  # e.g. logs
        LoResGround = 5  # unknown purpose; seems to randomly replace other ground types in lo-res
        Metal = 9  # e.g. grilles

        # rough
        ShallowWater = 20
        DeepWater = 21
        Killplane = 29  # or deathcam trigger, or lethal fall, etc.
        Trigger = 40  # other triggers?

        # NOTE: Offsets of 100, 200, and 300 appear to be used for stairs/sloped submeshes?

    def __post_init__(self):
        super(BaseWrappedHKX, self).__post_init__()
        self.map_collision_physics_data = MapCollisionPhysicsData(
            self.TYPES_MODULE, self.get_variant(0, *PHYSICS_DATA_T.__constraints__))

    @classmethod
    def from_meshes(
        cls,
        meshes: list[tuple[np.ndarray, np.ndarray]],
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
            template_path = HAVOK_PACKAGE_PATH("resources/MapCollisionTemplate2015.hkx")
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
                refCount=0,
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
                refCount=0,
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
