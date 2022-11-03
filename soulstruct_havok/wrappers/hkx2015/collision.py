from __future__ import annotations

import logging
from pathlib import Path
import typing as tp

from soulstruct.containers.dcx import DCXType

from soulstruct_havok.types.hk2015 import *
from soulstruct_havok.utilities.wavefront import read_obj
from soulstruct_havok.utilities.mopper import mopper
from soulstruct_havok.wrappers.base import BaseCollisionHKX
from .core import HKXMixin2015

_LOGGER = logging.getLogger(__name__)


class CollisionHKX(BaseCollisionHKX, HKXMixin2015):
    """Provies support for MOPP shapes and OBJ file conversion support for them."""

    physics_system: hkpPhysicsSystem

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
        """Validates type of collision shape and returns `meshstorage`."""
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

    @classmethod
    def from_meshes(
        cls,
        meshes: list[tuple[list[Vector4 | tp.Sequence[float, ...]], list[tp.Sequence[int, ...]]]],
        hkx_name: str,
        material_indices: tp.Sequence[int] = (),
        template_hkx: CollisionHKX = None,
        dcx_type: DCXType = DCXType.Null,
    ) -> CollisionHKX:
        """Convert a list of subpart meshes (vertices and faces) to a HKX collision file.

        Uses an existing HKX template file rather than constructing one from scratch. A custom template may also be
        supplied with `template_hkx`. Note that this custom template will be modified in place AND returned, not copied.

        Also uses default values for new mesh Havok classes, most of which don't matter or are empty. The one non-mesh
        property that really matters is `materialNameData`, which determines the material of the collision (for sounds,
        footsteps, terrain params, etc.) and can be supplied manually with `material_index`. If given, `material_index`
        must be a tuple with the same length as `meshes` (one material index per subpart).
        """
        if not meshes:
            raise ValueError("At least one mesh required to convert to HKX.")

        if template_hkx is None:
            # Use bundled template.
            hkx = cls(Path(__file__).parent / "../../resources/CollisionTemplate2015.hkx")
        else:
            hkx = template_hkx
        child_shape = hkx.get_child_shape()

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

        rigid_body = hkx.physics_system.rigidBodies[0]
        rigid_body.name = hkx_name

        # TODO: rigid_body.motion.motionState.objectRadius?

        child_shape.cachedNumChildShapes = sum(len(faces) for _, faces in meshes)
        child_shape.trianglesSubparts = []
        child_shape.meshstorage = []
        child_shape.materialArray = []
        for i, (vertices, faces) in enumerate(meshes):

            subpart = cls.get_subpart(len(vertices), len(faces))
            child_shape.trianglesSubparts.append(subpart)

            indices = []
            for face in faces:
                indices.extend(face)
                if len(face) == 3:
                    indices.append(0)
            storage = hkpStorageExtendedMeshShapeMeshSubpartStorage(
                memSizeAndFlags=0,
                refCount=0,
                vertices=[Vector4(*v[:3], 0.0) for v in vertices],
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

        # Havok docs say that embedded triangle subpart is only efficient for single-subpart shapes, but From disagrees.
        # Note that it is a fresh instance, not a copy of the first subpart.
        child_shape.embeddedTrianglesSubpart = cls.get_subpart(len(meshes[0][0]), len(meshes[0][1]))

        x_min = min([v[0] for mesh, _ in meshes for v in mesh])
        x_max = max([v[0] for mesh, _ in meshes for v in mesh])
        y_min = min([v[1] for mesh, _ in meshes for v in mesh])
        y_max = max([v[1] for mesh, _ in meshes for v in mesh])
        z_min = min([v[2] for mesh, _ in meshes for v in mesh])
        z_max = max([v[2] for mesh, _ in meshes for v in mesh])
        child_shape.aabbHalfExtents = Vector4((x_max - x_min) / 2, (y_max - y_min) / 2, (z_max - z_min) / 2, 0.0)
        child_shape.aabbCenter = Vector4((x_max + x_min) / 2, (y_max + y_min) / 2, (z_max + z_min) / 2, 0.0)

        hkx.regenerate_mopp_data()

        hkx.dcx_type = dcx_type

        return hkx

    @classmethod
    def from_obj(
        cls,
        obj_path: Path | str,
        hkx_name: str,
        material_index: tuple[int] = (),
        template_hkx: CollisionHKX = None,
        invert_x=True,
        dcx_type: DCXType = DCXType.Null,
    ) -> CollisionHKX:
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
            material_indices=material_index,
            template_hkx=template_hkx,
            dcx_type=dcx_type,
        )

    @staticmethod
    def get_subpart(vertices_count: int, faces_count: int):
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
            extrusion=Vector4(0.0, 0.0, 0.0, 0.0),
            transform=hkQsTransform(
                translation=Vector4(0.0, 0.0, 0.0, 0.0),
                rotation=(0.0, 0.0, 0.0, 1.0),
                scale=Vector4(1.0, 1.0, 1.0, 1.0),
            ),
        )

    def to_meshes(self) -> list[tuple[list[tuple[float, float, float]], list[tuple[int, ...]]]]:
        """Get a list of subpart meshes, each of which is a list of vertices (four floats) and a list of face tuples."""
        meshes = []  # type: list[tuple[list[tuple[float, float, float]], list[tuple[int, ...]]]]
        for i, mesh in enumerate(self.get_extended_mesh_meshstorage()):
            if len(mesh.indices16) % 4:
                raise ValueError("`indices16` length must be a multiple of 4.")
            vertices = [(vert.x, vert.y, vert.z) for vert in mesh.vertices]
            faces = []
            for f in range(len(mesh.indices16) // 4):
                face = tuple(mesh.indices16[4 * f:4 * f + 3])
                faces.append(face)
            meshes.append((vertices, faces))
        return meshes

    def to_obj(self, invert_x=True) -> str:
        """Convert raw vertices and triangle faces (zero-separated triplets) from HKX meshes to OBJ file.

        Inverts (negates) X axis by default, which should be reversed on import.
        """
        name = self.get_name()
        obj_lines = [
            f"# OBJ file generated by Soulstruct from HKX with path: {self.path}",
            f"# Internal name: {name}"
        ]
        global_v_i = 0

        for i, mesh in enumerate(self.get_extended_mesh_meshstorage()):
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
        Path(obj_path).write_text(self.to_obj())
