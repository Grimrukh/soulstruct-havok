from __future__ import annotations

import logging
import os
import subprocess as sp
from pathlib import Path

from soulstruct.containers.dcx import DCXType
from soulstruct.utilities.files import read_json

from soulstruct_havok.types.hk2015 import *
from soulstruct_havok.utilities.wavefront import read_obj
from ..base import BaseWrapperHKX
from .core import HKXMixin2015

_LOGGER = logging.getLogger(__name__)


class CollisionHKX(BaseWrapperHKX, HKXMixin2015):
    """Loads HKX objects used as terrain 'hit' geometry, found in `map/mAA_BB_CC_DD` folders."""

    MOPPER_PATH = Path(r"C:\Users\Scott\Downloads\mopper-master\mopper-master\Release\mopper.exe")

    physics_system: hkpPhysicsSystem

    def create_attributes(self):
        physics_data = self.get_variant_index(0, "hkpPhysicsData")
        self.physics_system = physics_data.systems[0]

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

    def regenerate_mopp_data(self):
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

        mopp = self.mopper(mopper_input, mode="-esm")
        new_mopp_code = mopp["hkpMoppCode"]["data"]
        new_offset = mopp["hkpMoppCode"]["offset"]
        mopp_code.data = new_mopp_code
        mopp_code.info.offset = Vector4(new_offset)

    def get_name(self) -> str:
        return self.physics_system.rigidBodies[0].name

    @classmethod
    def from_obj(
        cls,
        obj_path: Path | str,
        hkx_name: str,
        material_name_data: tuple[int] = (),
        template_hkx: CollisionHKX = None,
        invert_x=True,
        dcx_type: DCXType = DCXType.Null,
    ) -> CollisionHKX:
        """Convert an OBJ file containing vertices and faces for one or more meshes (subparts) to a HKX collision file.

        Uses default values for a bunch of fields, most of which don't matter. Also uses new and improved Mopper.

        If `template_hkx` is given, it will be used as the base for the new HKX, rather than the stock `template.hkx`.
        Note that if given, `template_hkx` will be modified in place AND returned.

        Inverts X axis by default, which should also be done in `to_obj()` if used again here (for accurate depiction
        in Blender, etc.).
        """
        obj_meshes = read_obj(obj_path, invert_x=invert_x)
        if not obj_meshes:
            raise ValueError("At least one mesh required in OBJ to convert to HKX.")

        if template_hkx is None:
            hkx = cls(Path(__file__).parent / "resources/CollisionTemplate2015.hkx")
        else:
            hkx = template_hkx
        child_shape = hkx.get_child_shape()
        if len(child_shape.meshstorage) != len(obj_meshes):
            raise ValueError(
                f"Number of OBJ meshes ({len(obj_meshes)}) does not match number of existing meshes in template "
                f"HKX ({len(child_shape.meshstorage)}). Omit `template_hkx` to allow any number of OBJ meshes."
            )

        if not material_name_data:
            material_name_data = [material.materialNameData for material in child_shape.materialArray]
        elif len(material_name_data) != len(obj_meshes):
            raise ValueError(
                f"Length of `material_name_data` ({len(material_name_data)}) does not match number of meshes in "
                f"OBJ ({len(obj_meshes)})."
            )
        else:
            material_name_data = [0] * len(obj_meshes)

        rigid_body = hkx.physics_system.rigidBodies[0]
        rigid_body.name = hkx_name

        # TODO: rigid_body.motion.motionState.objectRadius?

        child_shape.cachedNumChildShapes = sum(len(faces) for _, faces in obj_meshes)
        child_shape.trianglesSubparts = []
        child_shape.meshstorage = []
        child_shape.materialArray = []
        for i, (vertices, faces) in enumerate(obj_meshes):

            subpart = cls.get_subpart(len(vertices), len(faces))
            child_shape.trianglesSubparts.append(subpart)

            indices = []
            for face in faces:
                indices.extend(face)
            storage = hkpStorageExtendedMeshShapeMeshSubpartStorage(
                memSizeAndFlags=0,
                refCount=0,
                vertices=vertices,
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
                materialNameData=material_name_data[i],
            )
            child_shape.materialArray.append(material)

        # Havok docs say that embedded triangle subpart is only efficient for single-subpart shapes, but From disagrees.
        # Note that it is a fresh instance, not a copy of the first subpart.
        child_shape.embeddedTrianglesSubpart = cls.get_subpart(len(obj_meshes[0][0]), len(obj_meshes[0][1]))

        x_min = min([v.x for mesh, _ in obj_meshes for v in mesh])
        x_max = max([v.x for mesh, _ in obj_meshes for v in mesh])
        y_min = min([v.y for mesh, _ in obj_meshes for v in mesh])
        y_max = max([v.y for mesh, _ in obj_meshes for v in mesh])
        z_min = min([v.z for mesh, _ in obj_meshes for v in mesh])
        z_max = max([v.z for mesh, _ in obj_meshes for v in mesh])
        child_shape.aabbHalfExtents = Vector4((x_max - x_min) / 2, (y_max - y_min) / 2, (z_max - z_min) / 2, 0.0)
        child_shape.aabbCenter = Vector4((x_max + x_min) / 2, (y_max + y_min) / 2, (z_max + z_min) / 2, 0.0)

        hkx.regenerate_mopp_data()

        hkx.dcx_type = dcx_type

        return hkx

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

    @staticmethod
    def mopper(input_lines: list[str], mode: str) -> dict:
        if mode not in {"-ccm", "-msm", "-esm"}:
            raise ValueError("`mode` must be -ccm, -msm, or -esm.")
        if Path("mopp.json").exists():
            os.remove("mopp.json")
        input_text = "\n".join(input_lines) + "\n"
        # print(input_text)
        Path("mopper_input.txt").write_text(input_text)
        _LOGGER.info("# Running mopper...")
        sp.call([str(CollisionHKX.MOPPER_PATH), mode, "mopper_input.txt"])
        if not Path("mopp.json").exists():
            raise FileNotFoundError("Mopper did not produce `mopp.json`.")
        return read_json("mopp.json")
