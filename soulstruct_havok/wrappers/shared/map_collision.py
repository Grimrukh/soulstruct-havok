"""Map collision HKX wrappers for Dark Souls 1 (PTDE and DSR).

The changes in HKX format between these are minor, other than the Havok version (2010 vs. 2015) and packfile/tagfile
format. This class stores just the meshes and handles reading/writing of both for either version of DS1.
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
from dataclasses import dataclass
from enum import IntEnum
from pathlib import Path

import numpy as np
from soulstruct.base.game_file import GameFile
from soulstruct.utilities.binary import BinaryReader, BinaryWriter

from soulstruct_havok.core import HKX
from soulstruct_havok.enums import HavokVersion
from soulstruct_havok.types import hk2010, hk2015, hk2016
from soulstruct_havok.utilities.files import HAVOK_PACKAGE_PATH
from soulstruct_havok.utilities.maths import Vector4
from soulstruct_havok.utilities.mopper import mopper
from soulstruct_havok.utilities.wavefront import read_obj

_LOGGER = logging.getLogger("soulstruct_havok")

PHYSICS_DATA_T = tp.Union[
    hk2010.hkpPhysicsData,
    hk2015.hkpPhysicsData,
    hk2016.hkpPhysicsData,
]
PHYSICS_SYSTEM_T = tp.Union[
    hk2010.hkpPhysicsSystem,
    hk2015.hkpPhysicsSystem,
    hk2016.hkpPhysicsSystem,
]
CUSTOM_MESH_SHAPE_T = tp.Union[
    hk2010.CustomParamStorageExtendedMeshShape,
    hk2015.CustomMeshParameter,
    hk2016.CustomMeshParameter,
]
SUBPART_STORAGE_T = tp.Union[
    hk2010.hkpStorageExtendedMeshShapeMeshSubpartStorage,
    hk2015.hkpStorageExtendedMeshShapeMeshSubpartStorage,
    hk2016.hkpStorageExtendedMeshShapeMeshSubpartStorage,
]
TRIANGLES_SUBPART_T = tp.Union[
    hk2010.hkpExtendedMeshShapeTrianglesSubpart,
    hk2015.hkpExtendedMeshShapeTrianglesSubpart,
    hk2016.hkpExtendedMeshShapeTrianglesSubpart,
]
MOPP_CODE_T = tp.Union[
    hk2010.hkpMoppCode,
    hk2015.hkpMoppCode,
    hk2016.hkpMoppCode,
]


class MapCollisionMaterial(IntEnum):
    """Enum for material indices that are attached to HKX mesh subparts in DS1 (both versions).

    Offsets of 100, 200, and 300 from these base values appear to be used for stairs/sloped submeshes; they probably
    change the friction coefficient.

    TODO: Watch IW's awesome video on DS1 collision again.
    """
    Default = 0  # unknown usage
    Rock = 1  # actual rocks, bricks
    Stone = 2  # e.g. walls
    Grass = 3  # e.g. forest ground
    Wood = 4  # e.g. logs
    LoResGround = 5  # unknown purpose; seems to randomly replace other ground types in lo-res
    # TODO: 6 appears in unused/prototype/corrupted h1000B2A10 (Firelink).
    Metal = 9  # e.g. grilles

    # rough
    ShallowWater = 20
    DeepWater = 21
    Killplane = 29  # also deathcam trigger, or lethal fall, etc.
    Trigger = 40  # other triggers?


@dataclass(slots=True)
class MapCollisionModelMesh:
    vertices: np.ndarray  # (n, 3) `float32` array (fourth column from HKX dropped)
    faces: np.ndarray  # (m, 3) `uint16` array (fourth column from HKX dropped)
    material_index: int = 0  # material index for this submesh (see `MapCollisionMaterial`)

    @property
    def vertex_count(self):
        return self.vertices.shape[0]

    @property
    def face_count(self):
        return self.faces.shape[0]


@dataclass(slots=True)
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
    name: str
    # Each collision submesh is a tuple of `(vertices_array, faces_array, material_index)`.
    meshes: list[MapCollisionModelMesh]
    # Havok version of the model, which determines the HKX export format. Set on HKX import and can be changed.
    hk_version: HavokVersion

    @classmethod
    def from_reader(cls, reader: BinaryReader) -> tp.Self:
        """Just wraps `HKX` class."""
        hkx = HKX.from_reader(reader)
        return cls.from_hkx(hkx)

    @classmethod
    def from_hkx(cls, hkx: HKX) -> tp.Self:
        """Extract mesh vertices, faces, and material indices from HKX."""
        if hkx.hk_version not in {"2010", "2015", "2016"}:
            raise ValueError(f"Cannot import `MapCollisionModel` from HKX with Havok version: {hkx.hk_version}")

        physics_data, physics_system = cls.get_hkx_physics(hkx)
        if not physics_system.rigidBodies:
            raise ValueError("No rigid bodies found in HKX physics system.")
        name = physics_system.rigidBodies[0].name
        meshes = []
        child_shape = cls.get_child_shape(physics_system)
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

        for subpart_storage, material_index in zip(mesh_subparts, material_indices):
            if len(subpart_storage.indices16) % 4:
                raise ValueError("Collision HKX mesh subpart `indices16` length must be a multiple of 4.")
            vertices = subpart_storage.vertices[:, :3]  # drop fourth column
            face_count = len(subpart_storage.indices16) // 4
            faces = np.empty((face_count, 3), dtype=np.uint16)
            for f in range(face_count):
                index_0 = subpart_storage.indices16[4 * f]
                index_1 = subpart_storage.indices16[4 * f + 1]
                index_2 = subpart_storage.indices16[4 * f + 2]
                # NOTE: Index 3 in `mesh.indices16` quadruples is always 0, so we ignore it.
                faces[f] = [index_0, index_1, index_2]
            meshes.append(MapCollisionModelMesh(vertices, faces, material_index))

        return cls(name=name, meshes=meshes, hk_version=HavokVersion(hkx.hk_version))

    def to_writer(self) -> BinaryWriter:
        """Just wraps `HKX` class."""
        hkx = self.to_hkx()
        return hkx.to_writer()

    def to_hkx(self) -> HKX:
        """Use bundled template HKX of appropriate Havok version (from DS1) to insert mesh data into a new HKX file."""
        if not self.meshes:
            raise ValueError("Map collision has no `meshes`. Cannot convert to collision HKX.")

        # TODO: Template shouldn't strictly be necessary. I'm just too lazy to set up the full HKX structure."""
        match self.hk_version:
            case HavokVersion.hk2010:
                template_path = HAVOK_PACKAGE_PATH("resources/MapCollisionTemplate2010.hkx")
                hkx = HKX.from_path(template_path)
            case HavokVersion.hk2015:
                template_path = HAVOK_PACKAGE_PATH("resources/MapCollisionTemplate2015.hkx")
                hkx = HKX.from_path(template_path)
            case HavokVersion.hk2016:
                # TODO: What game did I even add hk2016 for...? Sekiro?
                raise NotImplementedError("Havok 2016 does not yet support MapCollisionModel export. (Need template.)")
            case _:
                raise ValueError(f"Cannot export `MapCollisionModel` to HKX for Havok version: {self.hk_version}")

        physics_data, physics_system = self.get_hkx_physics(hkx)

        # Name is assigned to rigid body.
        rigid_body = physics_system.rigidBodies[0]
        rigid_body.name = self.name
        # TODO: rigid_body.motion.motionState.objectRadius?

        # We only assign data (vertices, faces, material indices) to the `CustomParamStorageExtendedMeshShape`, which
        # is stored deep at `physicsData.systems[0].rigidBodies[0].collidable.shape.child.childShape`. (These collision
        # HKX files have only a single system, rigid body, and child shape.)
        child_shape = self.get_child_shape(physics_system)
        total_face_count = sum(mesh.face_count for mesh in self.meshes)
        child_shape.cachedNumChildShapes = total_face_count
        child_shape.trianglesSubparts = []
        child_shape.meshstorage = []
        child_shape.materialArray = []

        for mesh in self.meshes:

            vertices = mesh.vertices
            faces = mesh.faces

            subpart = self.new_triangles_subpart(len(vertices), len(faces))
            child_shape.trianglesSubparts.append(subpart)

            if vertices.shape[1] == 3:
                # Add fourth column of zeroes.
                vertices = np.hstack((vertices, np.zeros((mesh.vertex_count, 1), dtype=vertices.dtype)))

            if faces.shape[1] == 3:
                # Add fourth column of zeroes.
                faces = np.hstack((faces, np.zeros((mesh.face_count, 1), dtype=faces.dtype)))

            storage = self.new_subpart_storage(vertices, faces)
            child_shape.meshstorage.append(storage)

            kwargs = dict(
                version=37120,
                vertexDataBuffer=[255] * mesh.vertex_count,
                # TODO: `vertexDataStride` is a weird field I can't map out from the 2010 bytes.
                vertexDataStride=0 if self.hk_version == HavokVersion.hk2010 else 1,
                primitiveDataBuffer=[],
                materialNameData=mesh.material_index,
            )
            match self.hk_version:
                case HavokVersion.hk2010:
                    material = hk2010.CustomMeshParameter(**kwargs)
                case HavokVersion.hk2015:
                    material = hk2015.CustomMeshParameter(**kwargs)
                case HavokVersion.hk2016:
                    material = hk2016.CustomMeshParameter(**kwargs)
                case _:  # unreachable
                    raise ValueError(f"Cannot export `MapCollisionModel` to HKX for Havok version: {self.hk_version}")

            child_shape.materialArray.append(material)

        # Havok docs say that embedded triangle subpart is only efficient for single-subpart shapes, but FromSoft seems
        # to disagree (or just didn't care), because it is included for multi-subpart models. Note that the embedded
        # subpart is a fresh instance, NOT just a reference to the first subpart object from above.
        first_mesh = self.meshes[0]
        child_shape.embeddedTrianglesSubpart = self.new_triangles_subpart(
            first_mesh.vertex_count, first_mesh.face_count
        )

        # Get 3D mins/maxs of all vertices to calculate AABB. (`w = 0` added below.)
        vertex_mins = [mesh.vertices.min(axis=0) for mesh in self.meshes]
        vertex_maxs = [mesh.vertices.max(axis=0) for mesh in self.meshes]
        global_min = np.min(vertex_mins, axis=0)
        global_max = np.max(vertex_maxs, axis=0)
        half_extents = (global_max - global_min) / 2
        center = (global_max + global_min) / 2

        child_shape.aabbHalfExtents = Vector4([*half_extents, 0.0])
        child_shape.aabbCenter = Vector4([*center, 0.0])

        # Use Mopper executable to regenerate binary MOPP code.
        self.regenerate_mopp_data(physics_system)

        return hkx

    @staticmethod
    def get_hkx_physics(hkx: HKX) -> tuple[PHYSICS_DATA_T, PHYSICS_SYSTEM_T]:
        # noinspection PyTypeChecker
        physics_data = hkx.root.namedVariants[0].variant  # type: PHYSICS_DATA_T
        if not isinstance(physics_data, (hk2010.hkpPhysicsData, hk2015.hkpPhysicsData, hk2016.hkpPhysicsSystem)):
            raise TypeError(f"Expected HKX variant 0 to be `hkpPhysicsData`. Found: {physics_data.get_type_name()}")
        physics_system = physics_data.systems[0]  # type: PHYSICS_SYSTEM_T
        return physics_data, physics_system

    @staticmethod
    def get_child_shape(physics_system: PHYSICS_SYSTEM_T) -> CUSTOM_MESH_SHAPE_T:
        """Validates type of collision shape and returns `childShape`."""
        shape = physics_system.rigidBodies[0].collidable.shape
        if not isinstance(shape, (hk2010.hkpMoppBvTreeShape, hk2015.hkpMoppBvTreeShape, hk2016.hkpMoppBvTreeShape)):
            raise TypeError("Expected collision shape to be `hkpMoppBvTreeShape`.")
        child_shape = shape.child.childShape
        if not isinstance(
            child_shape,
            (
                hk2010.CustomParamStorageExtendedMeshShape,
                hk2015.CustomParamStorageExtendedMeshShape,
                hk2016.CustomParamStorageExtendedMeshShape,
            ),
        ):
            raise TypeError(
                f"Expected collision child shape to be `CustomParamStorageExtendedMeshShape`. "
                f"Found: {child_shape.__class__.__name__}"
            )
        return child_shape

    @staticmethod
    def get_mopp_code(physics_system: PHYSICS_SYSTEM_T) -> MOPP_CODE_T:
        shape = physics_system.rigidBodies[0].collidable.shape
        if not isinstance(
            shape,
            (
                hk2010.hkpMoppBvTreeShape,
                hk2015.hkpMoppBvTreeShape,
                hk2016.hkpMoppBvTreeShape,
            ),
        ):
            raise TypeError("Expected collision shape to be `hkpMoppBvTreeShape`.")
        return shape.code

    @classmethod
    def regenerate_mopp_data(cls, physics_system: PHYSICS_SYSTEM_T):
        """Use `mopper.exe` to build new MOPP code, including `code.info.offset` vector."""
        shape = cls.get_child_shape(physics_system)
        meshstorage = shape.meshstorage
        mopp_code = cls.get_mopp_code(physics_system)

        mopper_input = [f"{len(meshstorage)}"]
        for mesh in meshstorage:
            mopper_input.append("")
            mopper_input.append(f"{len(mesh.vertices)}")

            # Format array of vertices as "x y z" lines (lines already joined).
            v = io.StringIO()
            np.savetxt(v, mesh.vertices[:, :3], fmt="%r")
            mopper_input.append(v.getvalue())
            mopper_input.append("")  # blank line

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

    def new_subpart_storage(self, vertices: np.ndarray, faces: np.ndarray) -> SUBPART_STORAGE_T:
        """Create Havok 'subpart storage' class that stores the vertex positions and faces (vertex indices)."""
        kwargs = dict(
            # `referenceCount` / `refCount` defaults to 0
            vertices=vertices,
            indices8=[],
            indices16=faces.ravel().tolist(),
            indices32=[],
            materialIndices=[],
            materials=[],
            namedMaterials=[],
            materialIndices16=[],
        )
        match self.hk_version:
            case HavokVersion.hk2010:
                return hk2010.hkpStorageExtendedMeshShapeMeshSubpartStorage(**kwargs)
            case HavokVersion.hk2015:
                return hk2015.hkpStorageExtendedMeshShapeMeshSubpartStorage(**kwargs)
            case HavokVersion.hk2016:
                return hk2016.hkpStorageExtendedMeshShapeMeshSubpartStorage(**kwargs)
            case _:
                raise ValueError(f"Cannot export `MapCollisionModel` to HKX for Havok version: {self.hk_version}")

    def new_triangles_subpart(self, vertices_count: int, faces_count: int) -> TRIANGLES_SUBPART_T:
        """Returns a new `hkpExtendedMeshShapeTrianglesSubpart` with the given number of vertices and faces.

        All other members can be set to default values, fortunately (in DS1 at least).
        """
        kwargs = dict(
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
            triangleOffset=2010252431,  # TODO: should be given in `mopp.json` (but doesn't seem critical)
            indexStriding=8,
            stridingType=2,  # 16-bit
            flipAlternateTriangles=0,
            extrusion=Vector4.zero(),
        )
        match self.hk_version:
            case HavokVersion.hk2010:
                return hk2010.hkpExtendedMeshShapeTrianglesSubpart(
                    **kwargs,
                    transform=hk2010.hkQsTransform(),
                )
            case HavokVersion.hk2015:
                return hk2015.hkpExtendedMeshShapeTrianglesSubpart(
                    **kwargs,
                    transform=hk2015.hkQsTransform(),
                )
            case HavokVersion.hk2016:
                return hk2016.hkpExtendedMeshShapeTrianglesSubpart(
                    **kwargs,
                    transform=hk2016.hkQsTransform(),
                )
            case _:
                raise ValueError(f"Cannot export `MapCollisionModel` to HKX for Havok version: {self.hk_version}")

    @classmethod
    def from_obj_path(
        cls,
        obj_path: Path | str,
        material_indices: tuple[int] = (),
        hkx_name: str = "",
        invert_x=True,
        hk_version: str = "2015",
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
            hk_version=HavokVersion(hk_version),  # default
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
