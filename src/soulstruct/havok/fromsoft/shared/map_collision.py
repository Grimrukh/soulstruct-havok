"""Map collision HKX wrappers for MOPP-based `hkp` meshes used in Demon's Souls and Dark Souls 1 (PTDE/DSR).

The changes in HKX format between these are minor, other than the Havok version (5.5.0 / 2010 / 2015) and the use of
tagfile rather than packfile for DSR. This class stores just the meshes and handles reading/writing of both for the
different games. It is unified, rather than inherited per-game, to make usage with Blender wrapping easier.
"""
from __future__ import annotations

__all__ = [
    "MapCollisionMaterial",
    "MapCollisionModelMesh",
    "MapCollisionModel",
]

import io
import logging
import typing as tp
from dataclasses import dataclass, field
from enum import IntEnum
from pathlib import Path

import numpy as np
from soulstruct.base.game_file import GameFile
from soulstruct.utilities.binary import BinaryReader, BinaryWriter

from soulstruct.havok.core import HKX
from soulstruct.havok.enums import HavokModule
from soulstruct.havok.types import hk550, hk2010, hk2015
from soulstruct.havok.types.protocols.physics import *
from soulstruct.havok.utilities.files import SOULSTRUCT_HAVOK_PATH
from soulstruct.havok.utilities.maths import Vector4
from soulstruct.havok.utilities.mopper import mopper
from soulstruct.havok.utilities.wavefront import read_obj

_LOGGER = logging.getLogger(__name__)


class MapCollisionMaterial(IntEnum):
    """Enum for material indices that are attached to HKX mesh subparts in DS1 (both versions).

    Offsets of 100, 200, and 300 from these base values appear to be used for stairs/sloped submeshes; they probably
    change the friction coefficient.

    TODO: Watch IW's awesome video on DS1 collision again.

    TODO: Not confirmed for Demon's Souls (Havok 5.5.0) but looks good so far.
    """
    Dummy = 0  # unknown usage
    OutdoorStone = 1  # actual rocks, bricks
    IndoorStone = 2  # e.g. walls
    Soil = 3  # e.g. dirt, light grass
    Wood = 4  # e.g. logs
    Grass = 5  # used for heavy grass/foliage
    Gravel = 6
    Snow = 7
    Ice = 8  # Used for crystals in Crystal Caves
    Metal = 9  # e.g. grilles
    Sand = 10
    Bone = 11
    Ash = 12
    # no params for 13
    RottenWood = 14  # Used for the roof you fight Bell Gargoyles on.
    BigTree = 15  # Some wood in the Great Hollow
    # no params for 16
    SnowNoFootprint = 17
    # no params for 18
    WaterSlide = 19
    ShallowWater = 20
    DeepWater = 21
    Mucus = 22  # e.g. slime in The Depths
    PoisonSwamp = 23
    Mud = 24
    CoalTar = 25  # Used for the area at the bottom of Sen's Fortress with the Titanite Demons
    ChimeraSwamp = 26
    Lava = 27
    Carpet = 28
    Empty = 29  # Used for anything that is not meant to have a visual (killplane, deathcam, invisible wall, etc.)
    # No params for 30-33
    Wood2 = 34  # Identical param name to Wood, slightly different particles?
    # No params for 35-36
    Trigger = 40  # other triggers?

    # Legacy names:
    Default = 0
    Rock = 1
    Stone = 2


class DemonsSoulsFaceFlags(IntEnum):
    """Values attached to specifix mesh faces in Demon's Souls collisions (uint16)."""
    x0000 = 0x0000  # most common                (in mesh 0 of h0004b0)
    x0840 = 0x0840  # unknown = 0000100001000000 (in mesh 1 of h0004b0)
    x2A0B = 0x2A0B  # unknown = 0010101000001011 (in mesh 1 of h0004b0)
    x2A0C = 0x2A0C  # unknown = 0010101000001100 (in mesh 1 of h0004b0)
    x43F8 = 0x43F8  # unknown = 0100001111101111 (in mesh 0 of h0004b0)
    x43EF = 0x43EF  # unknown = 0100001111111000 (in mesh 0 of h0004b0)
    xFFFF = 0xFFFF  # unknown = 1111111111111111 (in mesh 1 of h0004b0) (could be 'all' or 'default')


@dataclass(slots=True)
class MapCollisionModelMesh:
    vertices: np.ndarray  # (n, 4) `float32` array directly from HKX (fourth column should be zeroes)
    faces: np.ndarray  # (m, 4) `uint16` array directly from HKX (fourth column could contain face data)
    material_index: int = 0  # material index for this submesh (see `MapCollisionMaterial`)

    @property
    def vertices3D(self):
        """Drop fourth column of vertices."""
        return self.vertices[:, :3]

    @property
    def vertex_count(self):
        return self.vertices.shape[0]

    @property
    def face_vertex_indices(self):
        """Drop fourth column of faces."""
        return self.faces[:, :3]

    @property
    def face_data(self):
        """Return fourth column of faces, which may contain special flags or just zeroes."""
        return self.faces[:, 3]

    @property
    def face_count(self):
        return self.faces.shape[0]

    @property
    def vertex_index_bit_size(self) -> int:
        return self.faces.dtype.itemsize * 8


class MapCollisionModel(GameFile):
    """
    Reduced representation of the simple meshes and material indices inside a map collision HKX file, while discarding
    everything that can be auto-generated on HKX export (e.g. unused HKX fields and new MOPP code).

    FromSoft map collisions use a custom shape data container called `CustomParamStorageExtendedMeshShape`, which
    gives each mesh a material ID that determines footstep sounds/VFX and other interactive properties.

    Each mesh has a special MOPP code that is generated by Havok to speed up collision detection. The MOPP code is
    stored in the `hkpMoppBvTreeShape` shape and is regenerated here using a bundled executable I compiled from the
    public Havok 2012 SDK, modified from a Niftools repo.

    Note that the name of the map collision is also stored inside the shape data.

    I'm not sure if games after (or before) DS1 use the MOPP code -- I suspect some of them use new `hknp` classes with
    even less scrutable detection methods -- so this class is attached to Havok 2015 (DSR) for now.
    """

    # Name of collision model, e.g. 'h1000B1', which appears internally inside the HKX (probably no in-game effect).
    name: str = "h0000B0"
    # Each collision submesh is a tuple of `(vertices_array, faces_array, material_index)`.
    meshes: list[MapCollisionModelMesh] = field(default_factory=list)
    # Havok version of the model, which determines the HKX export format. Set on HKX import and can be changed.
    havok_module: HavokModule = field(default=HavokModule.hk2015)
    # Indicates if this model will be exported as big-endian.
    is_big_endian: bool = False

    SUPPORTED_MODULES: tp.ClassVar[set[HavokModule]] = {
        HavokModule.hk550,
        HavokModule.hk2010,
        HavokModule.hk2015,
    }

    @classmethod
    def from_reader(cls, reader: BinaryReader) -> tp.Self:
        """Just wraps `HKX` class."""
        hkx = HKX.from_reader(reader)
        return cls.from_hkx(hkx)

    @classmethod
    def from_hkx(cls, hkx: HKX) -> tp.Self:
        """Extract mesh vertices, faces, and material indices from HKX."""
        if hkx.havok_module not in cls.SUPPORTED_MODULES:
            raise ValueError(f"Cannot import `MapCollisionModel` from HKX with Havok version: {repr(hkx.hk_version)}")

        physics_data, physics_system = cls.get_hkx_physics(hkx)
        if not physics_system.rigidBodies:
            raise ValueError("No rigid bodies found in HKX physics system.")
        name = physics_system.rigidBodies[0].name
        meshes = []
        child_shape, shape_type = cls.get_child_shape(physics_system)

        if shape_type == "CUSTOM":
            child_shape: FSCustomParamStorageExtendedMeshShape
            mesh_subparts = child_shape.meshstorage
            material_indices = tuple(material.materialNameData for material in child_shape.materialArray)
            if len(material_indices) > len(mesh_subparts):
                _LOGGER.warning(
                    f"Number of material indices ({len(material_indices)}) exceeds number of subparts "
                    f"({len(mesh_subparts)}). Ignoring excess materials."
                )
                material_indices = material_indices[:len(mesh_subparts)]
            elif len(material_indices) < len(mesh_subparts):
                _LOGGER.warning(
                    f"Number of material indices ({len(material_indices)}) is less than number of subparts "
                    f"({len(mesh_subparts)}). Excess subparts defaulting to material index 0."
                )
                excess_count = len(mesh_subparts) - len(material_indices)
                material_indices += (0,) * excess_count

            for subpart_storage, material_index in zip(mesh_subparts, material_indices, strict=True):
                vertices = subpart_storage.vertices  # already 4-column

                vertex_indices, face_dtype = cls.get_vertex_indices_and_dtype(subpart_storage)
                if len(vertex_indices) % 4:
                    raise ValueError("Collision HKX mesh subpart `indices{N}` length must be a multiple of 4.")
                faces = np.array(vertex_indices, dtype=face_dtype).reshape((-1, 4))

                meshes.append(MapCollisionModelMesh(vertices, faces, material_index))

        elif shape_type == "STORAGE_EXTENDED":
            # Check for a single material index in `meshstorage.materials`. Note that this array contains Havok material
            # definitions from Havok 2010 onwards, rather than the integers seen in Havok 5.5.0, which might explain why
            # FromSoft extended the class with their own simple integer material array (though even Demon's Souls uses
            # the custom class, and its materials are still just integers; perhaps they knew about the upcoming Havok
            # changes before Demon's Souls release).
            child_shape: StorageExtendedMeshShape
            material_indices_list = []
            for mesh_subpart in child_shape.meshstorage:
                if mesh_subpart.materials and isinstance(mesh_subpart.materials[0], int):
                    material_indices_list.append(mesh_subpart.materials[0])
                else:
                    material_indices_list.append(0)  # default for future export using custom class

            for subpart_storage, material_index in zip(child_shape.meshstorage, material_indices_list, strict=True):
                vertices = subpart_storage.vertices  # already 4-column

                vertex_indices, face_dtype = cls.get_vertex_indices_and_dtype(subpart_storage)
                if len(vertex_indices) % 4:
                    raise ValueError("Collision HKX mesh subpart `indices{N}` length must be a multiple of 4.")
                faces = np.array(vertex_indices, dtype=face_dtype).reshape((-1, 4))

                meshes.append(MapCollisionModelMesh(vertices, faces, material_index))

        elif shape_type == "STORAGE":
            # See above. The `hkpStorageMeshShape` class was dropped at some point (maybe Havok 2010?) and probably
            # never switched from integer materials to Havok classes, but we check nonetheless.
            child_shape: StorageMeshShape
            material_indices_list = []
            for mesh_subpart in child_shape.storage:  # no `meshstorage` and `shapestorage`
                if mesh_subpart.materials and isinstance(mesh_subpart.materials[0], int):
                    material_indices_list.append(mesh_subpart.materials[0])
                else:
                    material_indices_list.append(0)  # default for future export using custom class

            for subpart_storage, material_index in zip(child_shape.storage, material_indices_list, strict=True):

                # Vertices are a flattened array of float triples. We add the fourth column for consistency.
                vertices_3d = np.reshape(subpart_storage.vertices, (-1, 3))
                vertices = np.concatenate((vertices_3d, np.zeros((vertices_3d.shape[0], 1), dtype=np.float32)), axis=1)

                vertex_indices, face_dtype = cls.get_vertex_indices_and_dtype(subpart_storage)
                if len(vertex_indices) % 3:
                    raise ValueError(
                        "Collision HKX mesh subpart `indices{N}` length must be a multiple of 3 (old storage class)."
                    )
                # Faces are index triples. We add a fourth column for face data.
                faces = np.array(vertex_indices, dtype=face_dtype).reshape((-1, 3))
                faces = np.concatenate((faces, np.zeros((faces.shape[0], 1), dtype=face_dtype)), axis=1)

                meshes.append(MapCollisionModelMesh(vertices, faces, material_index))

        else:
            # Shouldn't be reachable.
            raise ValueError(f"Unknown shape type: {shape_type}")

        return cls(name=name, meshes=meshes, havok_module=hkx.havok_module, is_big_endian=hkx.is_big_endian)

    def to_writer(self) -> BinaryWriter:
        """Just wraps `HKX` class."""
        hkx = self.to_hkx()
        return hkx.to_writer()

    def to_hkx(self) -> HKX:
        """Use bundled template HKX of appropriate Havok version to insert mesh data into a new HKX file."""
        if not self.meshes:
            raise ValueError("Map collision has no `meshes`. Cannot convert to collision HKX.")

        # Template is the easiest way to set up the full HKX structure. (These are the only three games that use MOPP.)
        match self.havok_module:
            case HavokModule.hk550:
                template_path = SOULSTRUCT_HAVOK_PATH("havok/resources/MapCollisionTemplate_DES.hkx")
                hkx = HKX.from_path(template_path)
            case HavokModule.hk2010:
                template_path = SOULSTRUCT_HAVOK_PATH("havok/resources/MapCollisionTemplate_PTDE.hkx")
                hkx = HKX.from_path(template_path)
            case HavokModule.hk2015:
                template_path = SOULSTRUCT_HAVOK_PATH("havok/resources/MapCollisionTemplate_DSR.hkx")
                hkx = HKX.from_path(template_path)
            case _:
                raise ValueError(f"Cannot export `MapCollisionModel` to HKX for Havok version: {self.havok_module}")

        physics_data, physics_system = self.get_hkx_physics(hkx)

        # Name is assigned to rigid body.
        rigid_body = physics_system.rigidBodies[0]
        rigid_body.name = self.name
        # TODO: rigid_body.motion.motionState.objectRadius?

        # We only assign data (vertices, faces, material indices) to the `CustomParamStorageExtendedMeshShape`, which
        # is stored deep at `physicsData.systems[0].rigidBodies[0].collidable.shape.child.childShape`. (These collision
        # HKX files have only a single system, rigid body, and child shape.)
        child_shape, _ = self.get_child_shape(physics_system)  # template always has custom material data
        total_face_count = sum(mesh.face_count for mesh in self.meshes)
        if hasattr(child_shape, "cachedNumChildShapes"):
            child_shape.cachedNumChildShapes = total_face_count
        child_shape.trianglesSubparts = []
        child_shape.meshstorage = []
        child_shape.materialArray = []

        for mesh in self.meshes:

            subpart = self.new_triangles_subpart(mesh)
            child_shape.trianglesSubparts.append(subpart)

            storage = self.new_subpart_storage(mesh)
            child_shape.meshstorage.append(storage)

            kwargs = dict(
                version=37120,  # true for all supported games (DeS, DS1)
                vertexDataBuffer=[255] * mesh.vertex_count,
                materialNameData=mesh.material_index,
            )
            # Remaining `CustomMeshParameter` kwargs are module-specific.
            match self.havok_module:
                case HavokModule.hk550:
                    kwargs |= {"zero0": 0, "zero1": 0, "zero2": 0, "zero3": 0, "zero4": 0}
                    material = hk550.CustomMeshParameter(**kwargs)
                case HavokModule.hk2010:
                    kwargs |= {"zero0": 0, "zero1": 0, "zero2": 0, "zero3": 0, "zero4": 0}
                    material = hk2010.CustomMeshParameter(**kwargs)
                case HavokModule.hk2015:
                    kwargs |= {"vertexDataStride": 1, "primitiveDataBuffer": []}
                    material = hk2015.CustomMeshParameter(**kwargs)
                case _:  # unreachable
                    raise ValueError(
                        f"Cannot export `MapCollisionModel` to HKX for Havok version: {self.havok_module}"
                    )

            child_shape.materialArray.append(material)

        # Havok docs say that embedded triangle subpart is only efficient for single-subpart shapes, but FromSoft seems
        # to disagree (or just didn't care), because it is included for multi-subpart models. Note that the embedded
        # subpart is a fresh instance, NOT just a reference to the first subpart object from above.
        first_mesh = self.meshes[0]
        child_shape.embeddedTrianglesSubpart = self.new_triangles_subpart(first_mesh)

        # Get 3D mins/maxs of all vertices to calculate AABB. (`w = 0` added below.)
        vertex_mins = [mesh.vertices.min(axis=0) for mesh in self.meshes]
        vertex_maxs = [mesh.vertices.max(axis=0) for mesh in self.meshes]
        global_min = np.min(vertex_mins, axis=0)
        global_max = np.max(vertex_maxs, axis=0)
        half_extents = (global_max - global_min) / 2
        center = (global_max + global_min) / 2

        child_shape.aabbHalfExtents = Vector4(half_extents)
        child_shape.aabbCenter = Vector4(center)

        # Use Mopper executable to regenerate binary MOPP code.
        self.regenerate_mopp_data(physics_system)

        return hkx

    @staticmethod
    def get_vertex_indices_and_dtype(
        subpart_storage: StorageExtendedMeshShapeMeshSubpartStorage | StorageMeshShapeSubpartStorage
    ) -> tuple[np.ndarray, np.dtype]:
        if indices8 := getattr(subpart_storage, "indices8", []):
            # This HKX uses 8-bit indices. (Never observed and probably never will.)
            vertex_indices = indices8
            face_dtype = np.dtype("uint8")
            if subpart_storage.indices16:
                raise ValueError("Collision HKX mesh subpart has both `indices8` and `indices16` data.")
            if subpart_storage.indices32:
                raise ValueError("Collision HKX mesh subpart has both `indices8` and `indices32` data.")
        elif subpart_storage.indices16:
            # This HKX uses 16-bit indices.
            vertex_indices = subpart_storage.indices16
            face_dtype = np.dtype("uint16")
            if subpart_storage.indices32:
                raise ValueError("Collision HKX mesh subpart has both `indices16` and `indices32` data.")
        elif subpart_storage.indices32:
            # This HKX uses 32-bit indices.
            vertex_indices = subpart_storage.indices32
            face_dtype = np.dtype("uint32")
        else:
            raise ValueError("Collision HKX mesh subpart has no `indices8`, `indices16`, or `indices32` data.")

        return vertex_indices, face_dtype

    # noinspection PyTypeChecker
    @staticmethod
    def get_hkx_physics(hkx: HKX) -> tuple[PhysicsData, PhysicsSystem]:
        physics_data = hkx.root.namedVariants[0].variant  # type: PhysicsData
        if physics_data.get_type_name() != "hkpPhysicsData":
            raise TypeError(f"Expected HKX variant 0 to be `hkpPhysicsData`. Found: {physics_data.get_type_name()}")
        physics_system = physics_data.systems[0]  # type: PhysicsSystem
        return physics_data, physics_system

    # noinspection PyTypeChecker
    @staticmethod
    def get_child_shape(physics_system: PhysicsSystem) -> tuple[FSCustomParamStorageExtendedMeshShape, str]:
        """Validates type of collision shape and returns `childShape`, along with a string indicating if the shape uses
        FromSoft's custom subclass `CustomParamStorageExtendedMeshShape` (which includes material name data), the base
        Havok `hkpStorageExtendedMeshShape`, or the even older Havok `hkpStorageMeshShape`.

        NOTE: Some old collisions may just use `hkpStorageExtendedMeshShape` rather than FromSoft's custom subclass that
        adds 'material name data'. We support that here too, but only on import - the custom subclass is always used on
        export, as the game will need it to function. Submesh materials should be assigned manually in this case, as
        they will default to zero if absent. (In other words, free restoration of cut content!)
        """
        shape = physics_system.rigidBodies[0].collidable.shape  # type: MoppBvTreeShape
        if shape.get_type_name() != "hkpMoppBvTreeShape":
            raise TypeError(f"Expected collision shape to be `hkpMoppBvTreeShape`, not: {shape.get_type_name()}.")
        child_shape = shape.child.childShape  # type: FSCustomParamStorageExtendedMeshShape
        if child_shape.get_type_name() != "CustomParamStorageExtendedMeshShape":
            if child_shape.get_type_name() == "hkpStorageExtendedMeshShape":
                # Pre-custom class is supported, will just have no material data.
                return child_shape, "STORAGE_EXTENDED"
            if child_shape.get_type_name() == "hkpStorageMeshShape":
                # Pre-custom, non-extended class is supported, will just have no material data.
                return child_shape, "STORAGE"
            raise TypeError(
                f"Expected collision child shape to be `CustomParamStorageExtendedMeshShape`, not: "
                f"{child_shape.get_type_name()}"
            )
        return child_shape, "CUSTOM"

    # noinspection PyTypeChecker
    @staticmethod
    def get_mopp_code(physics_system: PhysicsSystem) -> MoppCode:
        shape = physics_system.rigidBodies[0].collidable.shape  # type: MoppBvTreeShape
        if shape.get_type_name() != "hkpMoppBvTreeShape":
            raise TypeError("Expected collision shape to be `hkpMoppBvTreeShape`.")
        return shape.code

    def regenerate_mopp_data(self, physics_system: PhysicsSystem):
        """Use `mopper.exe` to build new MOPP code, including `code.info.offset` vector.

        Works for Demon's Souls, Dark Souls: PTDE, and Dark Souls: Remastered. Games after DS1 use `hkcd` classes
        rather than MOPP code and are currently impossible to build/export.
        """
        shape, _ = self.get_child_shape(physics_system)
        meshstorage = shape.meshstorage
        mopp_code = self.get_mopp_code(physics_system)

        mopper_input = [f"{len(meshstorage)}"]
        for mesh in meshstorage:
            if not mesh.indices16:
                raise ValueError("Cannot regenerate MOPP code for mesh with no 16-bit vertex indices.")
            mopper_input.append("")
            mopper_input.append(f"{len(mesh.vertices)}")

            # Format array of vertices as "x y z" lines (lines already joined).
            v = io.StringIO()
            np.savetxt(v, mesh.vertices[:, :3], fmt="%r")
            mopper_input.append(v.getvalue())
            mopper_input.append("")  # blank line

            face_count = len(mesh.indices16) // 4
            mopper_input.append(f"{face_count}")
            for f in range(face_count):
                # Write first three elements only.
                i = f * 4
                mopper_input.append(f"{mesh.indices16[i]} {mesh.indices16[i + 1]} {mesh.indices16[i + 2]}")

        mopp = mopper(mopper_input, mode="-esm")
        new_mopp_code = mopp["hkpMoppCode"]["data"]
        new_offset = mopp["hkpMoppCode"]["offset"]
        mopp_code.data = new_mopp_code
        mopp_code.info.offset = Vector4(new_offset)

    def new_subpart_storage(self, mesh: MapCollisionModelMesh) -> StorageExtendedMeshShapeMeshSubpartStorage:
        """Create Havok 'subpart storage' class that stores the vertex positions and faces (vertex indices)."""

        if mesh.vertices.shape[1] == 3:
            # Add fourth column of zeroes.
            vertices = np.hstack((mesh.vertices, np.zeros((mesh.vertex_count, 1), dtype=mesh.vertices.dtype)))
        else:
            vertices = mesh.vertices

        if mesh.faces.shape[1] == 3:
            # Add fourth column of zeroes.
            faces = np.hstack((mesh.faces, np.zeros((mesh.face_count, 1), dtype=mesh.faces.dtype)))
        else:
            faces = mesh.faces
        vertex_indices = faces.ravel().tolist()  # flatten to list

        kwargs = dict(
            # `referenceCount` / `refCount` defaults to 0
            vertices=vertices,
            indices16=[],
            indices32=[],
            materialIndices=[],
            materials=[],
            materialIndices16=[],
        )

        if self.havok_module == HavokModule.hk550:
            if mesh.vertex_index_bit_size == 8:
                raise ValueError("Havok 550 does not support 8-bit mesh vertex indices.")
            kwargs[f"indices{mesh.vertex_index_bit_size}"] = vertex_indices
            return hk550.hkpStorageExtendedMeshShapeMeshSubpartStorage(**kwargs)

        kwargs |= dict(
            indices8=[],
            namedMaterials=[],
        )
        kwargs[f"indices{mesh.vertex_index_bit_size}"] = vertex_indices

        match self.havok_module:
            case HavokModule.hk2010:
                return hk2010.hkpStorageExtendedMeshShapeMeshSubpartStorage(**kwargs)
            case HavokModule.hk2015:
                return hk2015.hkpStorageExtendedMeshShapeMeshSubpartStorage(**kwargs)

        raise ValueError(f"Cannot export `MapCollisionModel` to HKX for Havok version: {self.havok_module}")

    def new_triangles_subpart(self, mesh: MapCollisionModelMesh) -> ExtendedMeshShapeTrianglesSubpart:
        """Returns a new `hkpExtendedMeshShapeTrianglesSubpart` with the given number of vertices and faces.

        All other members can be set to default values, fortunately (in DS1 at least).
        """
        kwargs = dict(
            materialStriding=0,
            materialIndexStriding=0,
            numTriangleShapes=mesh.face_count,
            vertexStriding=16,
            numVertices=mesh.vertex_count,
            extrusion=Vector4.zero(),
            indexStriding=8,
            flipAlternateTriangles=0,
            triangleOffset=-1,  # hard-coded offset in HKX files, but not needed
        )
        # Remaining fields are module-specific.
        match self.havok_module:
            case HavokModule.hk550:
                kwargs |= dict(
                    type=0,
                    materialIndexStridingType=1,
                    stridingType=1,
                    numMaterials=1,  # TODO: always 1?
                )
                return hk550.hkpExtendedMeshShapeTrianglesSubpart(**kwargs)
            case HavokModule.hk2010:
                kwargs |= dict(
                    typeAndFlags=2,
                    shapeInfo=0,
                    userData=0,
                    stridingType=2,
                    transform=hk2010.hkQsTransform(),
                )
                return hk2010.hkpExtendedMeshShapeTrianglesSubpart(**kwargs)
            case HavokModule.hk2015:
                kwargs |= dict(
                    typeAndFlags=2,
                    shapeInfo=0,
                    userData=0,
                    stridingType=2,
                    transform=hk2015.hkQsTransform(),
                )
                return hk2015.hkpExtendedMeshShapeTrianglesSubpart(**kwargs)

        raise ValueError(f"Cannot export `MapCollisionModel` to HKX for Havok version: {self.havok_module}")

    @classmethod
    def from_obj_path(
        cls,
        obj_path: Path | str,
        material_indices: tuple[int] = (),
        hkx_name: str = "",
        invert_x=True,
        havok_module=HavokModule.hk2015,
    ) -> tp.Self:
        """Read meshes from an OBJ file, with manually supplied material indices of the same length as the meshes.

        Material indices will all default to 0 if not given.

        `invert_x=True` by default, which should also be done in `to_obj()` if used again here (e.g. for accurate
        depiction in Blender).
        """
        if not material_indices:
            # Try to read from OBJ header.
            obj_lines = Path(obj_path).read_text().split("\n")
            for line in obj_lines:
                line = line.strip()
                if not line.startswith("#"):
                    break  # header done
                elif line.startswith("# Material indices: "):
                    material_indices = tuple(int(m) for m in line.split(":")[1].strip().split(","))
                    break

        obj_meshes = read_obj(obj_path, invert_x=invert_x)
        if not obj_meshes:
            raise ValueError("At least one mesh required in OBJ to convert to HKX.")

        if material_indices:
            if len(material_indices) != len(obj_meshes):
                raise ValueError(
                    f"Number of `material_indices` ({len(material_indices)}) must match number of meshes in OBJ file "
                    f"({len(obj_meshes)}) or be zero."
                )
        else:
            material_indices = [0] * len(obj_meshes)
        hkx_name = hkx_name or Path(obj_path).stem.split(".")[0]

        meshes = [
            MapCollisionModelMesh(vertices, faces, material_index)
            for (vertices, faces), material_index in zip(obj_meshes, material_indices)
        ]

        return cls(
            name=hkx_name,
            meshes=meshes,
            havok_module=havok_module,
        )

    def to_obj(self, invert_x=True) -> str:
        """Convert raw vertices and triangle faces (zero-separated triplets) from HKX meshes to OBJ file.

        Inverts (negates) X axis by default, which should be reversed on import. Also note that vertices in OBJ files
        are 1-indexed by the face indices. Material indices are stored in header.
        """
        obj_lines = [
            f"# OBJ file generated by Soulstruct from HKX with name: {self.name}",
            f"# Material indices: {', '.join(str(mesh.material_index) for mesh in self.meshes)}",
        ]
        global_v_i = 0

        for i, mesh in enumerate(self.meshes):
            obj_lines += ["", f"o {self.name} Subpart {i}"]
            for vert in mesh.vertices:
                obj_lines.append(f"v {-vert.x if invert_x else vert.x} {vert.y} {vert.z}")
            obj_lines.append("s off")
            face_offset = global_v_i + 1  # 1-indexed vertices
            for face in mesh.faces:
                obj_lines.append(f"f {face_offset + face[0]} {face_offset + face[1]} {face_offset + face[2]}")
            global_v_i += len(mesh.vertices)

        return "\n".join(obj_lines) + "\n"

    def write_obj(self, obj_path: Path | str):
        """Write OBJ file to `obj_path`."""
        Path(obj_path).write_text(self.to_obj())

    def __repr__(self) -> str:
        lines = [
            "MapCollisionModel(",
            f"    name=\"{self.name}\",",
            f"    havok_module={repr(self.havok_module)},",
            f"    meshes=[",
        ]
        for mesh in self.meshes:
            lines.append("        MapCollisionModelMesh(")
            vertices = str(mesh.vertices).replace("\n", "\n                    ")
            faces = str(mesh.faces).replace("\n", "\n                 ")
            lines.append(f"           material_index={mesh.material_index},")
            lines.append(f"           vertices={vertices} <{len(mesh.vertices)}>,")
            lines.append(f"           faces={faces} <{len(mesh.faces)}>,")
            lines.append("        ),")
        lines.append("    ],")
        lines.append(")")
        return "\n".join(lines)
