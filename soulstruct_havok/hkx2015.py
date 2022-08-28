from __future__ import annotations

import os
import re
import subprocess as sp
import typing as tp
from pathlib import Path

from soulstruct.containers import Binder
from soulstruct.containers.dcx import DCXType
from soulstruct.utilities.maths import QuatTransform
from soulstruct.utilities.files import read_json

from soulstruct_havok.core import HKX
from soulstruct_havok.types.hk2015 import *
from soulstruct_havok.spline_compression import SplineCompressedAnimationData


class HKX2015(HKX):

    root: hkRootLevelContainer

    def __init__(self, file_source, dcx_type: None | DCXType = DCXType.Null, compendium: None | HKX = None):
        super().__init__(file_source, dcx_type=dcx_type, compendium=compendium, hk_format=self.TAGFILE)
        self.create_attributes()

    def create_attributes(self):
        pass


class SkeletonHKX(HKX2015):
    """Loads HKX objects that are found in a "Skeleton" HKX file (inside `anibnd` binder, usually `Skeleton.HKX`)."""

    animationContainer: hkaAnimationContainer
    skeleton: hkaSkeleton

    def create_attributes(self):
        self.skeleton = self.animationContainer.skeletons[0]

    def scale(self, factor: float):
        """Scale all bone translations in place by `factor`."""
        for pose in self.skeleton.referencePose:
            pose.translation = tuple(x * factor for x in pose.translation)

    @classmethod
    def from_anibnd(cls, anibnd_path: Path | str, prefer_bak=False) -> SkeletonHKX:
        anibnd_path = Path(anibnd_path)
        anibnd = Binder(anibnd_path, from_bak=prefer_bak)
        return cls(anibnd[1000000])


class AnimationHKX(HKX2015):
    """Loads HKX objects that are found in an "Animation" HKX file (inside `anibnd` binder, e.g. `a00_3000.hkx`)."""

    animationContainer: hkaAnimationContainer
    animation: hkaAnimation
    animationBinder: hkaAnimationBinding
    reference_frame_samples: list[Vector4]

    def create_attributes(self):
        self.set_variant_attribute("animationContainer", hkaAnimationContainer, 0)
        self.animation = self.animationContainer.animations[0]
        self.animation_binding = self.animationContainer.bindings[0]
        if isinstance(self.animation, hkaSplineCompressedAnimation) and self.animation.extractedMotion:
            reference_frame = self.animation.extractedMotion
            if isinstance(reference_frame, hkaDefaultAnimatedReferenceFrame):
                self.reference_frame_samples = reference_frame.referenceFrameSamples

    def get_spline_compressed_animation_data(self) -> SplineCompressedAnimationData:
        if isinstance(self.animation, hkaSplineCompressedAnimation):
            return SplineCompressedAnimationData(
                data=self.animation.data,
                transform_track_count=self.animation.numberOfTransformTracks,
                block_count=self.animation.numBlocks,
            )
        raise TypeError("Animation is not spline-compressed. Cannot get data.")

    def decompress_spline_animation_data(self) -> list[list[QuatTransform]]:
        """Convert spline-compressed animation data to a list of lists (per track) of `QuatTransform` instances."""
        if isinstance(self.animation, hkaSplineCompressedAnimation):
            return self.get_spline_compressed_animation_data().to_transform_track_lists(
                frame_count=self.animation.numFrames,
                max_frames_per_block=self.animation.maxFramesPerBlock
            )
        raise TypeError("Animation is not spline-compressed. Cannot decompress data.")

    def scale(self, factor: float):
        """Modifies all spline/static animation tracks, and also root motion (reference frame samples)."""
        if not isinstance(self.animation, hkaSplineCompressedAnimation):
            raise TypeError("Animation is not spline-compressed. Cannot scale data.")
        scaled_data = self.get_spline_compressed_animation_data().get_scaled_animation_data(factor)
        self.animation.data = scaled_data

        # Root motion (if present), sans W.
        if self.reference_frame_samples:
            for sample in self.reference_frame_samples:
                # Scale X, Y, and Z only, not W.
                sample.x *= factor
                sample.y *= factor
                sample.z *= factor

    def reverse(self):
        """Reverses all control points in all spline tracks, and also root motion (reference frame samples)."""
        if not isinstance(self.animation, hkaSplineCompressedAnimation):
            raise TypeError("Animation is not spline-compressed. Cannot reverse data.")
        reversed_data = self.get_spline_compressed_animation_data().get_reversed_animation_data()
        self.animation.data = reversed_data

        # Root motion (if present).
        if self.reference_frame_samples:
            extracted_motion = self.animation.extractedMotion
            if isinstance(extracted_motion, hkaDefaultAnimatedReferenceFrame):
                extracted_motion.referenceFrameSamples = list(reversed(self.reference_frame_samples))

    @property
    def root_motion(self):
        """Usual modding alias for reference frame samples."""
        return self.reference_frame_samples

    @classmethod
    def from_anibnd(
        cls, anibnd_path: Path | str, animation_id: tp.Union[int, str], prefer_bak=False
    ) -> AnimationHKX:
        if isinstance(animation_id, int):
            prefix = animation_id // 10000 * 10000
            base_id = animation_id % 10000
            animation_path = f"a{prefix:02d}_{base_id:04d}.hkx"
        else:
            animation_path = animation_id
            if not animation_path.endswith(".hkx"):
                animation_path += ".hkx"
        anibnd_path = Path(anibnd_path)
        anibnd = Binder(anibnd_path, from_bak=prefer_bak)
        return cls(anibnd[animation_path])


class RagdollHKX(HKX2015):
    """Loads HKX objects that are found in a "Ragdoll" HKX file (inside `chrbnd` binder, e.g. `c0000.hkx`)."""

    animationContainer: hkaAnimationContainer
    standard_skeleton: hkaSkeleton
    ragdoll_skeleton: hkaSkeleton
    physicsData: hkpPhysicsData
    ragdollInstance: hkaRagdollInstance
    ragdoll_to_standard_skeleton_mapper: hkaSkeletonMapper
    standard_to_ragdoll_skeleton_mapper: hkaSkeletonMapper

    def create_attributes(self):
        self.set_variant_attribute("animationContainer", hkaAnimationContainer, 0)
        self.standard_skeleton = self.animationContainer.skeletons[0]
        self.ragdoll_skeleton = self.animationContainer.skeletons[1]
        self.set_variant_attribute("physicsData", hkpPhysicsData, 1)
        self.set_variant_attribute("ragdollInstance", hkaRagdollInstance, 2)
        # TODO: Is this the correct order?
        self.set_variant_attribute("ragdoll_to_standard_skeleton_mapper", hkaSkeletonMapper, 3)
        self.set_variant_attribute("standard_to_ragdoll_skeleton_mapper", hkaSkeletonMapper, 4)

    def scale(self, factor: float):
        """Scale all translation information, including:
            - bones in both the standard and ragdoll skeletons
            - rigid body collidables
            - motion state transforms and swept transforms
            - skeleton mapper transforms in both directions

        This is currently working well, though since actual "ragdoll mode" only occurs when certain enemies die, any
        mismatched (and probably harmless) physics will be more of an aesthetic issue.
        """
        for pose in self.standard_skeleton.referencePose:
            pose.translation = tuple(x * factor for x in pose.translation)
        for pose in self.ragdoll_skeleton.referencePose:
            pose.translation = tuple(x * factor for x in pose.translation)

        for rigid_body in self.physicsData.systems[0].rigidBodies:
            scale_shape(rigid_body.collidable.shape, factor)

            # TODO: motion inertiaAndMassInv?

            motion_state = rigid_body.motion.motionState
            motion_state.transform.translation.x *= factor
            motion_state.transform.translation.y *= factor
            motion_state.transform.translation.z *= factor  # not W
            motion_state.objectRadius *= factor

            swept_transform = motion_state.sweptTransform
            swept_transform[0] *= factor
            swept_transform[1] *= factor
            # Indices 2 and 3 are rotations.
            swept_transform[4] *= factor

        # TODO: constraint instance transforms?

        for mapper in (self.ragdoll_to_standard_skeleton_mapper, self.standard_to_ragdoll_skeleton_mapper):
            for simple in mapper.mapping.simpleMappings:
                simple.aFromBTransform.translation *= factor
            for chain in mapper.mapping.chainMappings:
                chain.startAFromBTransform.translation *= factor

    @classmethod
    def from_chrbnd(cls, chrbnd_path: Path | str, prefer_bak=False) -> RagdollHKX:
        chrbnd_path = Path(chrbnd_path)
        if (bak_path := chrbnd_path.with_suffix(chrbnd_path.suffix + ".bak")).is_file() and prefer_bak:
            chrbnd_path = bak_path
        chrbnd = Binder(chrbnd_path)
        model_name = chrbnd_path.name.split(".")[0]  # e.g. "c0000"
        return cls(chrbnd[f"{model_name}.hkx"])


class ClothHKX(HKX2015):
    """Loads HKX objects that are found in a "Cloth" HKX file (inside `chrbnd` binder, e.g. `c2410_c.hkx`).

    This file is not used for every character - only those with cloth physics (e.g. capes).
    """

    physicsData: hkpPhysicsData

    def create_attributes(self):
        self.set_variant_attribute("physicasData", hkpPhysicsData, 0)

    def scale(self, factor: float):
        """Scale all translation information, including:
            - rigid body collidables
            - motion state transforms and swept transforms

        TODO: Since cloth is always in "ragdoll" mode, forces may need to be updated more cautiously here.
        """
        for rigid_body in self.physicsData.systems[0].rigidBodies:
            scale_shape(rigid_body.collidable.shape, factor)

            # TODO: motion inertiaAndMassInv?

            motion_state = rigid_body.motion.motionState
            motion_state.transform.translation.x *= factor
            motion_state.transform.translation.y *= factor
            motion_state.transform.translation.z *= factor  # not W
            motion_state.objectRadius *= factor

            swept_transform = motion_state.sweptTransform
            swept_transform[0] *= factor
            swept_transform[1] *= factor
            # Indices 2 and 3 are rotations.
            swept_transform[4] *= factor

        for constraint_instance in self.physicsData.systems[0].constraints:

            # TODO: Missing some types here.

            constraint_instance.data.link_0_pivot_b_velocity

            try:
                infos = constraint_instance.data.infos
            except AttributeError:
                pass
            else:
                for info in infos:
                    info.pivot_in_a = tuple(x * factor for x in info.pivot_in_a)
                    info.pivot_in_b = tuple(x * factor for x in info.pivot_in_b)
                constraint_instance.data.link_0_pivot_b_velocity = tuple(
                    x * factor for x in constraint_instance.data.link_0_pivot_b_velocity
                )
                # TODO: scale tau, damping, cfm?
                constraint_instance.data.max_error_distance *= factor
                constraint_instance.data.inertia_per_meter *= factor

            try:
                atoms = constraint_instance.data.atoms
            except AttributeError:
                continue

            if "transforms" in atoms.node.value:
                transforms = atoms.transforms

                old_transform_A = transforms.transform_a.to_flat_column_order()
                scaled_translate = tuple(x * factor for x in old_transform_A[12:15]) + (1.0,)
                transforms.node.value["transformA"].value = tuple(old_transform_A[:12]) + scaled_translate

                old_transform_B = transforms.transform_b.to_flat_column_order()
                scaled_translate = tuple(x * factor for x in old_transform_B[12:15]) + (1.0,)
                transforms.node.value["transformB"].value = tuple(old_transform_B[:12]) + scaled_translate

            if "pivots" in atoms.node.value:
                pivots = atoms.pivots

                scaled_translate = tuple(x * factor for x in pivots.translation_a)
                pivots.node.value["translationA"].value = scaled_translate

                scaled_translate = tuple(x * factor for x in pivots.translation_b)
                pivots.node.value["translationB"].value = scaled_translate

            if "spring" in atoms.node.value:
                spring = atoms.spring
                spring.length *= factor
                spring.max_length *= factor

    @classmethod
    def from_chrbnd(cls, chrbnd_path: Path | str, prefer_bak=False) -> ClothHKX:
        chrbnd_path = Path(chrbnd_path)
        if (bak_path := chrbnd_path.with_suffix(chrbnd_path.suffix + ".bak")).is_file() and prefer_bak:
            chrbnd_path = bak_path
        chrbnd = Binder(chrbnd_path)
        model_name = chrbnd_path.name.split(".")[0]  # e.g. "c0000"
        try:
            return cls(chrbnd[f"{model_name}_c.hkx"])
        except KeyError:
            raise FileNotFoundError(f"No '*_c.hkx' cloth physics file found in chrbnd {chrbnd_path}.")


class CollisionHKX(HKX2015):
    """Loads HKX objects used as terrain 'hit' geometry, found in `map/mAA_BB_CC_DD` folders."""

    MOPPER_PATH = Path(r"C:\Users\Scott\Downloads\mopper-master\mopper-master\Release\mopper.exe")

    physicsData: hkpPhysicsData

    def create_attributes(self):
        self.set_variant_attribute("physicsData", hkpPhysicsData, 0)

    def get_child_shape(self) -> CustomParamStorageExtendedMeshShape:
        """Validates type of collision shape and returns `childShape`."""
        shape = self.physicsData.systems[0].rigidBodies[0].collidable.shape
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
        shape = self.physicsData.systems[0].rigidBodies[0].collidable.shape
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
        return self.physicsData.systems[0].rigidBodies[0].name

    @classmethod
    def from_binder(cls, binder_path: Path | str, entry_name: str, from_bak=False):
        """Pull HKX from binder. (Probably not that useful if you want to write that same binder back.)"""
        binder = Binder(binder_path, from_bak=from_bak)
        entry = binder.find_entry_matching_name(entry_name)
        return cls(entry)

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

        if template_hkx is not None:
            hkx = template_hkx if template_hkx is not None else cls("template.hkx")
            child_shape = hkx.get_child_shape()
            if len(child_shape.meshstorage) != len(obj_meshes):
                raise ValueError(
                    f"Number of OBJ meshes ({len(obj_meshes)}) does not match number of existing meshes in template "
                    f"HKX ({len(child_shape.meshstorage)}). Omit `template_hkx` to allow any number of OBJ meshes."
                )
        else:
            hkx = cls("template.hkx")
            child_shape = hkx.get_child_shape()

        if not material_name_data:
            material_name_data = [material.materialNameData for material in child_shape.materialArray]
        elif len(material_name_data) != len(obj_meshes):
            raise ValueError(
                f"Length of `material_name_data` ({len(material_name_data)}) does not match number of meshes in "
                f"OBJ ({len(obj_meshes)})."
            )
        else:
            material_name_data = [0] * len(obj_meshes)

        rigid_body = hkx.physicsData.systems[0].rigidBodies[0]
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
        print("# Running mopper...")
        sp.call([str(CollisionHKX.MOPPER_PATH), mode, "mopper_input.txt"])
        if not Path("mopp.json").exists():
            raise FileNotFoundError("Mopper did not produce `mopp.json`.")
        return read_json("mopp.json")


# TODO: Move to some utility module.
def scale_shape(shape: hkpShape, factor: float):
    if isinstance(shape, hkpConvexShape):
        shape.radius *= factor
        if isinstance(shape, hkpCapsuleShape):
            shape.vertexA *= factor
            shape.vertexB *= factor
    elif isinstance(shape, hkpMoppBvTreeShape):
        scale_shape(shape.child.childShape, factor)
    elif isinstance(shape, hkpExtendedMeshShape):
        shape.embeddedTrianglesSubpart.transform.translation *= factor
        shape.aabbHalfExtents *= factor
        shape.aabbCenter *= factor
        if isinstance(shape, hkpStorageExtendedMeshShape):
            for mesh in shape.meshstorage:
                for vertex in mesh.vertices:
                    vertex *= factor


def read_obj(obj_path: Path | str, invert_x=True) -> list[tuple[list[Vector4], list[tuple[int, int, int]]]]:
    meshes = []  # type: list[tuple[list[Vector4], list[tuple[int, int, int]]]]
    mesh = None  # type: None | tuple[list, list]

    o_re = re.compile(r"^o .*$")
    v_re = re.compile(r"^v ([-\d.]+) ([-\d.]+) ([-\d.]+)$")
    f_re = re.compile(r"^f (\d+)(?://\d+)? (\d+)(?://\d+)? (\d+)(?://\d+)?$")

    global_v_i = 0

    with Path(obj_path).open("r") as f:
        for line in f.readlines():
            if o_re.match(line):
                if mesh is not None:
                    global_v_i += len(mesh[0])  # increase global vertex count
                mesh = ([], [])  # vertices, faces
                meshes.append(mesh)
            elif v := v_re.match(line):
                if mesh is None:
                    raise ValueError("Found 'v' vertex line before an 'o' object definition.")
                if mesh[1]:
                    raise ValueError("Found 'v' vertex line after 'f' face lines.")
                x, y, z = float(v.group(1)), float(v.group(2)), float(v.group(3))
                vertex = Vector4((-x if invert_x else x), y, z, 0.0)
                mesh[0].append(vertex)
            elif f := f_re.match(line):
                if mesh is None:
                    raise ValueError("Found 'f' face line before an 'o' object definition.")
                if not mesh[0]:
                    raise ValueError("Found 'f' face line before a 'v' vertex lines.")
                # Switch to 0-indexing, localize vertex indices, and insert zero that appears between triplets.
                face = (
                    int(f.group(1)) - global_v_i - 1,
                    int(f.group(2)) - global_v_i - 1,
                    int(f.group(3)) - global_v_i - 1,
                    0,
                )
                mesh[1].append(face)
            else:
                pass  # ignore all other lines

    return meshes
